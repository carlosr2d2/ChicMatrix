from collections import defaultdict
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Price, Product, Retailer, User
from app.schemas.schemas import (
  PriceComparison,
  ProductResponse,
  RecommendationItem,
)


class RecommendationEngine:
  """Hybrid recommender: rule-based filters + simple collaborative signals."""

  def __init__(self, db: Session):
    self.db = db

  def recommend(self, user: User, limit: int = 12) -> list[RecommendationItem]:
    products = self.db.query(Product).all()
    if not products:
      return []

    preferences = user.preferences or {}
    habits = user.habits or {}
    preferred_colors = {c.lower() for c in preferences.get("colors", [])}
    preferred_brands = {b.lower() for b in preferences.get("brands", [])}
    preferred_categories = {c.lower() for c in habits.get("occasions", [])}

    collaborative_scores = self._collaborative_scores(user)

    scored: list[tuple[Product, float, list[str]]] = []
    for product in products:
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

      size_score, size_reason = self._size_fit_score(user, product)
      score += size_score
      if size_reason:
        reasons.append(size_reason)

      collab = collaborative_scores.get(product.id, 0.0)
      if collab > 0:
        score += collab
        reasons.append("Popular among similar profiles")

      if score > 0:
        scored.append((product, score, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:limit] if scored else [(p, 0.5, ["Curated pick"]) for p in products[:limit]]

    return [self._build_item(product, score, reasons) for product, score, reasons in top]

  def _build_item(
    self, product: Product, score: float, reasons: list[str]
  ) -> RecommendationItem:
    prices = self._price_comparisons(product)
    best = min(prices, key=lambda p: p.amount) if prices else None
    return RecommendationItem(
      product=ProductResponse.model_validate(product),
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
