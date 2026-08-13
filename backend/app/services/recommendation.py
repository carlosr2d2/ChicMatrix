from collections import defaultdict
from datetime import datetime
import re

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.enums import SexCode
from app.models.models import Price, Product, ProductStyleTag, Retailer, User
from app.schemas.schemas import (
  PriceComparison,
  ProductResponse,
  ProductStyleTagOut,
  RecommendationItem,
)
from app.services.image_cache import absolute_image_url


class RecommendationEngine:
  """Hybrid recommender: rule-based filters + simple collaborative signals."""

  _FEMALE_MARKERS = re.compile(
    r"\b(women|woman|mujer|ladies|lady|womens|women's|for women)\b",
    re.IGNORECASE,
  )
  _MALE_MARKERS = re.compile(
    r"\b(men|man|hombre|gents|mens|men's|for men)\b",
    re.IGNORECASE,
  )
  _FEMALE_GARMENTS = re.compile(
    r"\b(dress|dresses|skirt|skirts|blouse|blouses|gown|gowns|leggings)\b",
    re.IGNORECASE,
  )

  def __init__(self, db: Session):
    self.db = db

  def recommend(self, user: User, limit: int = 12) -> list[RecommendationItem]:
    products = (
      self.db.query(Product)
      .options(joinedload(Product.style_assignments).joinedload(ProductStyleTag.tag))
      .all()
    )
    if not products:
      return []

    preferences = user.preferences or {}
    habits = user.habits or {}
    preferred_colors = {c.lower() for c in preferences.get("colors", [])}
    preferred_brands = {b.lower() for b in preferences.get("brands", [])}
    preferred_styles = {s.lower() for s in preferences.get("styles", [])}
    preferred_categories = {c.lower() for c in habits.get("occasions", [])}
    eligible = [p for p in products if self._is_sex_compatible(user, p)]

    collaborative_scores = self._collaborative_scores(user)

    scored: list[tuple[Product, float, list[str]]] = []
    for product in eligible:
      score = 0.0
      reasons: list[str] = []

      if product.color and product.color.lower() in preferred_colors:
        score += 2.0
        reasons.append(f"Matches preferred color: {product.color}")

      if product.brand and product.brand.lower() in preferred_brands:
        score += 2.5
        reasons.append(f"Preferred brand: {product.brand}")

      if product.category and product.category.lower() in preferred_categories:
        score += 1.5
        reasons.append(f"Suitable for occasion: {product.category}")

      style_score, style_reasons = self._style_match_score(product, preferred_styles)
      score += style_score
      reasons.extend(style_reasons)

      size_score, size_reason = self._size_fit_score(user, product)
      score += size_score
      if size_reason:
        reasons.append(size_reason)

      sex_score, sex_reason = self._sex_match_score(user, product)
      score += sex_score
      if sex_reason:
        reasons.append(sex_reason)

      collab = collaborative_scores.get(product.id, 0.0)
      if collab > 0:
        score += collab
        reasons.append("Popular among similar profiles")

      if score > 0:
        scored.append((product, score, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    if scored:
      top = scored[:limit]
    else:
      top = [(p, 0.5, ["Curated pick"]) for p in eligible[:limit]]

    return [self._build_item(product, score, reasons) for product, score, reasons in top]

  def _style_match_score(
    self, product: Product, preferred_styles: set[str]
  ) -> tuple[float, list[str]]:
    if not preferred_styles:
      return 0.0, []

    score = 0.0
    reasons: list[str] = []
    for assignment in product.style_assignments:
      tag = assignment.tag
      if not tag or not tag.active:
        continue
      if tag.code.lower() not in preferred_styles:
        continue
      score += 2.0 * float(assignment.score)
      reasons.append(f"Matches style: {tag.label_es}")
    return score, reasons

  def _build_item(
    self, product: Product, score: float, reasons: list[str]
  ) -> RecommendationItem:
    prices = self._price_comparisons(product)
    best = min(prices, key=lambda p: p.amount) if prices else None
    product_payload = ProductResponse.model_validate(product)
    product_payload = product_payload.model_copy(
      update={
        "image_url": absolute_image_url(product.image_url),
        "style_tags": [
          ProductStyleTagOut(
            code=assignment.tag.code,
            label_es=assignment.tag.label_es,
            score=assignment.score,
            model_version=assignment.model_version,
          )
          for assignment in sorted(
            product.style_assignments,
            key=lambda a: a.score,
            reverse=True,
          )
          if assignment.tag is not None
        ]
      }
    )
    return RecommendationItem(
      product=product_payload,
      score=round(score, 2),
      reasons=reasons,
      prices=prices,
      best_price=best,
    )

  def _price_comparisons(self, product: Product) -> list[PriceComparison]:
    rows = (
      self.db.query(Price, Product, Retailer)
      .join(Product, Price.product_id == Product.id)
      .join(Retailer, Price.retailer_id == Retailer.id)
      .filter(
        func.lower(Product.name) == func.lower(product.name),
        Product.brand == product.brand,
      )
      .order_by(Price.scraped_at.desc())
      .all()
    )

    seen_retailers: set[int] = set()
    comparisons: list[PriceComparison] = []
    for price, _prod, retailer in rows:
      if price.retailer_id in seen_retailers:
        continue
      seen_retailers.add(price.retailer_id)
      comparisons.append(
        PriceComparison(
          retailer_id=price.retailer_id,
          retailer_name=retailer.name,
          amount=price.amount,
          currency=price.currency,
          scraped_at=price.scraped_at,
        )
      )
    return comparisons

  def _size_fit_score(self, user: User, product: Product) -> tuple[float, str | None]:
    if not user.height_cm or not user.weight_kg:
      return 0.0, None

    bmi = user.weight_kg / ((user.height_cm / 100) ** 2)
    proportions = user.body_proportions or {}

    if product.category and product.category.lower() in {"outerwear", "coats", "jackets"}:
      if 18.5 <= bmi <= 25:
        return 1.0, "Good outerwear fit for your build"
      return 0.3, None

    if proportions.get("waist_cm") and product.size:
      return 0.8, f"Size {product.size} aligned with your measurements"

    return 0.2, None

  def _product_text(self, product: Product) -> str:
    return " ".join(
      part
      for part in [product.name or "", product.description or "", product.category or ""]
      if part
    )

  def _product_audience(self, product: Product) -> str | None:
    """Infer intended audience: female, male, or None (unisex/unknown)."""
    text = self._product_text(product)
    if not text:
      return None

    has_female = bool(self._FEMALE_MARKERS.search(text))
    # Avoid matching the "men" inside "women".
    text_without_women = self._FEMALE_MARKERS.sub(" ", text)
    has_male = bool(self._MALE_MARKERS.search(text_without_women))

    if has_female and not has_male:
      return SexCode.FEMALE.value
    if has_male and not has_female:
      return SexCode.MALE.value
    if has_female and has_male:
      return None
    if self._FEMALE_GARMENTS.search(text):
      return SexCode.FEMALE.value
    return None

  def _is_sex_compatible(self, user: User, product: Product) -> bool:
    sex = (user.sex or "").lower()
    if sex not in {SexCode.FEMALE.value, SexCode.MALE.value}:
      return True
    audience = self._product_audience(product)
    if audience is None:
      return True
    return audience == sex

  def _sex_match_score(self, user: User, product: Product) -> tuple[float, str | None]:
    """Boost when assortment explicitly matches profile sex."""
    sex = (user.sex or "").lower()
    if sex not in {SexCode.FEMALE.value, SexCode.MALE.value}:
      return 0.0, None
    audience = self._product_audience(product)
    if audience == sex == SexCode.FEMALE.value:
      return 1.5, "Aligned with women's assortment"
    if audience == sex == SexCode.MALE.value:
      return 1.5, "Aligned with men's assortment"
    return 0.0, None

  def _collaborative_scores(self, user: User) -> dict[int, float]:
    """Simple CF: users with similar BMI/category prefs boost shared product categories."""
    all_users = self.db.query(User).filter(User.id != user.id).all()
    user_cats = set((user.habits or {}).get("occasions", []))
    category_product_counts: dict[str, int] = defaultdict(int)

    for other in all_users:
      other_cats = set((other.habits or {}).get("occasions", []))
      overlap = len(user_cats & other_cats)
      if overlap == 0:
        continue

      other_prefs = (other.preferences or {}).get("brands", [])
      for brand in other_prefs:
        count = (
          self.db.query(Product)
          .filter(func.lower(Product.brand) == brand.lower())
          .count()
        )
        products = self.db.query(Product).filter(
          func.lower(Product.brand) == brand.lower()
        )
        for p in products:
          category_product_counts[p.id] += overlap * 0.5

    return dict(category_product_counts)
