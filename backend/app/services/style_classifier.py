"""Rule-based multi-label style classifier (F0)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.enums import StyleCode

MODEL_VERSION = "rules-v1"
DEFAULT_THRESHOLD = 0.45
MAX_TAGS = 4

# Weighted lexicon: phrase/token -> contribution toward a style score (0..1 capped later).
LEXICON: dict[StyleCode, list[tuple[str, float]]] = {
    StyleCode.FORMAL: [
        ("blazer", 0.45),
        ("tailored", 0.4),
        ("suit", 0.5),
        ("office", 0.35),
        ("evening gown", 0.45),
        ("gown", 0.3),
        ("silk midi", 0.3),
        ("formal", 0.5),
        ("sastre", 0.45),
        ("oficina", 0.35),
        ("elegante", 0.25),
        ("pleated silk", 0.3),
    ],
    StyleCode.SPORT: [
        ("sport", 0.45),
        ("athletic", 0.45),
        ("athleisure", 0.5),
        ("running", 0.45),
        ("gym", 0.4),
        ("performance", 0.35),
        ("training", 0.35),
        ("deporte", 0.45),
        ("deportivo", 0.45),
        ("dry-fit", 0.35),
        ("sneakers", 0.2),
    ],
    StyleCode.BIKER: [
        ("biker", 0.55),
        ("motorcycle", 0.5),
        ("moto", 0.45),
        ("motociclista", 0.55),
        ("harness", 0.35),
        ("rider", 0.3),
        ("leather biker", 0.55),
    ],
    StyleCode.ROCKER: [
        ("rocker", 0.5),
        ("rock", 0.35),
        ("punk", 0.45),
        ("metal", 0.35),
        ("band tee", 0.4),
        ("distressed", 0.3),
        ("studded", 0.35),
        ("leather jacket", 0.4),
        ("denim jacket", 0.25),
    ],
    StyleCode.CASUAL: [
        ("casual", 0.45),
        ("everyday", 0.35),
        ("crewneck", 0.3),
        ("denim", 0.3),
        ("jeans", 0.35),
        ("knit", 0.25),
        ("weekend", 0.3),
        ("relaxed", 0.25),
        ("dress", 0.3),
        ("top", 0.25),
        ("tshirt", 0.4),
        ("t-shirt", 0.4),
        ("shirt", 0.25),
    ],
    StyleCode.MINIMAL: [
        ("minimal", 0.5),
        ("minimalist", 0.55),
        ("clean lines", 0.4),
        ("contemporary", 0.3),
        ("understated", 0.35),
        ("neutral", 0.25),
        ("structured wool", 0.25),
    ],
    StyleCode.STREETWEAR: [
        ("streetwear", 0.55),
        ("street wear", 0.5),
        ("oversized", 0.4),
        ("hoodie", 0.4),
        ("graphic tee", 0.35),
        ("urban", 0.3),
        ("drop shoulder", 0.3),
    ],
}


@dataclass(frozen=True)
class StyleTagScore:
    tag: str
    score: float


@dataclass(frozen=True)
class ClassificationResult:
    tags: list[StyleTagScore]
    model_version: str
    rejected: list[str]


class StyleClassifier:
    """F0 multi-label classifier using a closed lexicon over name/description/brand."""

    def __init__(self, threshold: float = DEFAULT_THRESHOLD, max_tags: int = MAX_TAGS):
        self.threshold = threshold
        self.max_tags = max_tags

    def classify(
        self,
        *,
        name: str,
        description: str | None = None,
        brand: str | None = None,
        category: str | None = None,
        color: str | None = None,
        locale: str | None = None,  # reserved for F1
    ) -> ClassificationResult:
        text = " ".join(
            part for part in [name, description or "", brand or "", category or "", color or ""] if part
        ).lower()
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return ClassificationResult(tags=[], model_version=MODEL_VERSION, rejected=[])

        scores: dict[str, float] = {}
        for style, phrases in LEXICON.items():
            total = 0.0
            for phrase, weight in phrases:
                if phrase in text:
                    total += weight
            if total > 0:
                scores[style.value] = min(total, 1.0)

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        accepted: list[StyleTagScore] = []
        rejected: list[str] = []
        for tag, score in ranked:
            if score < self.threshold:
                rejected.append(tag)
                continue
            if len(accepted) >= self.max_tags:
                rejected.append(tag)
                continue
            accepted.append(StyleTagScore(tag=tag, score=round(score, 2)))

        return ClassificationResult(
            tags=accepted,
            model_version=MODEL_VERSION,
            rejected=rejected,
        )
