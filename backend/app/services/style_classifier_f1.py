"""TF-IDF centroid multi-label style classifier (F1, pure Python)."""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from app.models.enums import StyleCode
from app.services.style_classifier import (
    MAX_TAGS,
    ClassificationResult,
    StyleClassifier,
    StyleTagScore,
)

MODEL_VERSION = "nlp-tfidf-v1"
DEFAULT_THRESHOLD = 0.18
DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "style_models" / "f1_tfidf_v1.json"
)

_TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ]+", re.IGNORECASE)
STYLE_CODES = [c.value for c in StyleCode]


def build_text(
    *,
    name: str,
    description: str | None = None,
    brand: str | None = None,
    category: str | None = None,
    color: str | None = None,
) -> str:
    return " ".join(
        part for part in [name, description or "", brand or "", category or "", color or ""] if part
    )


def tokenize(text: str) -> list[str]:
    tokens = [t.lower() for t in _TOKEN_RE.findall(text or "")]
    if not tokens:
        return []
    grams = list(tokens)
    grams.extend(f"{a}_{b}" for a, b in zip(tokens, tokens[1:]))
    return grams


def _dot(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())


def _norm(vec: dict[str, float]) -> float:
    return math.sqrt(sum(v * v for v in vec.values())) or 1e-12


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    return _dot(a, b) / (_norm(a) * _norm(b))


@dataclass
class TfidfModel:
    model_version: str
    idf: dict[str, float]
    centroids: dict[str, dict[str, float]]
    threshold: float
    max_tags: int
    train_size: int
    train_subsets: list[str]

    def vectorize(self, text: str) -> dict[str, float]:
        counts = Counter(tokenize(text))
        if not counts:
            return {}
        total = float(sum(counts.values()))
        vec: dict[str, float] = {}
        for term, count in counts.items():
            idf = self.idf.get(term)
            if idf is None:
                continue
            vec[term] = (count / total) * idf
        return vec


def train_tfidf_model(
    rows: list[dict],
    *,
    threshold: float = DEFAULT_THRESHOLD,
    max_tags: int = MAX_TAGS,
    min_df: int = 2,
) -> TfidfModel:
    docs_tokens: list[list[str]] = []
    docs_tags: list[set[str]] = []
    for row in rows:
        text = build_text(
            name=row.get("name") or "",
            description=row.get("description"),
            brand=row.get("brand"),
            category=row.get("category"),
            color=row.get("color"),
        )
        tokens = tokenize(text)
        docs_tokens.append(tokens)
        docs_tags.append(set(row.get("gold_tags") or []))

    df: Counter[str] = Counter()
    for tokens in docs_tokens:
        df.update(set(tokens))

    n_docs = max(len(docs_tokens), 1)
    idf: dict[str, float] = {
        term: math.log((1 + n_docs) / (1 + count)) + 1.0
        for term, count in df.items()
        if count >= min_df
    }

    # Temporary model for vectorize helper.
    draft = TfidfModel(
        model_version=MODEL_VERSION,
        idf=idf,
        centroids={},
        threshold=threshold,
        max_tags=max_tags,
        train_size=len(rows),
        train_subsets=sorted({str(r.get("subset") or "unknown") for r in rows}),
    )

    sums: dict[str, dict[str, float]] = {code: defaultdict(float) for code in STYLE_CODES}
    counts: dict[str, int] = {code: 0 for code in STYLE_CODES}
    for tokens, tags in zip(docs_tokens, docs_tags):
        if not tags:
            continue
        # Rebuild sparse tf-idf from tokens using shared idf.
        counts_tok = Counter(tokens)
        total = float(sum(counts_tok.values())) or 1.0
        vec = {
            term: (count / total) * idf[term]
            for term, count in counts_tok.items()
            if term in idf
        }
        for tag in tags:
            if tag not in sums:
                continue
            counts[tag] += 1
            bucket = sums[tag]
            for term, value in vec.items():
                bucket[term] += value

    centroids: dict[str, dict[str, float]] = {}
    for tag, bucket in sums.items():
        n = counts[tag] or 1
        centroids[tag] = {term: value / n for term, value in bucket.items()}

    return TfidfModel(
        model_version=MODEL_VERSION,
        idf=idf,
        centroids=centroids,
        threshold=threshold,
        max_tags=max_tags,
        train_size=len(rows),
        train_subsets=draft.train_subsets,
    )


def save_model(model: TfidfModel, path: Path | None = None) -> Path:
    target = path or DEFAULT_MODEL_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_version": model.model_version,
        "idf": model.idf,
        "centroids": model.centroids,
        "threshold": model.threshold,
        "max_tags": model.max_tags,
        "train_size": model.train_size,
        "train_subsets": model.train_subsets,
    }
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def load_model(path: Path | None = None) -> TfidfModel:
    target = path or DEFAULT_MODEL_PATH
    if not target.is_file():
        raise FileNotFoundError(f"F1 model not found: {target}")
    payload = json.loads(target.read_text(encoding="utf-8"))
    return TfidfModel(
        model_version=payload.get("model_version") or MODEL_VERSION,
        idf=payload["idf"],
        centroids=payload["centroids"],
        threshold=float(payload.get("threshold", DEFAULT_THRESHOLD)),
        max_tags=int(payload.get("max_tags", MAX_TAGS)),
        train_size=int(payload.get("train_size", 0)),
        train_subsets=list(payload.get("train_subsets") or []),
    )


class StyleClassifierF1:
    """F1 multi-label classifier: TF-IDF cosine vs per-style centroids."""

    def __init__(
        self,
        model: TfidfModel | None = None,
        model_path: Path | None = None,
        threshold: float | None = None,
        max_tags: int | None = None,
    ):
        self.model = model or load_model(model_path)
        self.threshold = threshold if threshold is not None else self.model.threshold
        self.max_tags = max_tags if max_tags is not None else self.model.max_tags

    @property
    def model_version(self) -> str:
        return self.model.model_version

    def classify(
        self,
        *,
        name: str,
        description: str | None = None,
        brand: str | None = None,
        category: str | None = None,
        color: str | None = None,
        locale: str | None = None,
    ) -> ClassificationResult:
        _ = locale
        text = build_text(
            name=name,
            description=description,
            brand=brand,
            category=category,
            color=color,
        )
        vec = self.model.vectorize(text)
        if not vec:
            return ClassificationResult(tags=[], model_version=self.model_version, rejected=[])

        scores: dict[str, float] = {}
        for tag, centroid in self.model.centroids.items():
            if not centroid:
                continue
            scores[tag] = cosine(vec, centroid)

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
            accepted.append(StyleTagScore(tag=tag, score=round(float(score), 2)))

        return ClassificationResult(
            tags=accepted,
            model_version=self.model_version,
            rejected=rejected,
        )


class StyleClassifierHybrid:
    """F0-first hybrid: keep lexicon precision, fall back to F1 NLP when F0 is empty."""

    def __init__(
        self,
        f0: StyleClassifier | None = None,
        f1: StyleClassifierF1 | None = None,
        max_tags: int = MAX_TAGS,
        model_version: str = "hybrid-f0-f1-v1",
    ):
        self.f0 = f0 or StyleClassifier()
        self.f1 = f1 or StyleClassifierF1()
        self.max_tags = max_tags
        self.model_version = model_version

    def classify(
        self,
        *,
        name: str,
        description: str | None = None,
        brand: str | None = None,
        category: str | None = None,
        color: str | None = None,
        locale: str | None = None,
    ) -> ClassificationResult:
        kwargs = dict(
            name=name,
            description=description,
            brand=brand,
            category=category,
            color=color,
            locale=locale,
        )
        r0 = self.f0.classify(**kwargs)
        if r0.tags:
            return ClassificationResult(
                tags=r0.tags[: self.max_tags],
                model_version=self.model_version,
                rejected=r0.rejected,
            )
        r1 = self.f1.classify(**kwargs)
        return ClassificationResult(
            tags=r1.tags[: self.max_tags],
            model_version=self.model_version,
            rejected=r1.rejected,
        )
