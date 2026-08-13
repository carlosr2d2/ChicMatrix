"""Evaluate StyleClassifier F0 against the frozen gold set."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from app.models.enums import StyleCode
from app.services.style_classifier import MODEL_VERSION, StyleClassifier

GOLD_SET_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "style_gold" / "gold_set.jsonl"
STYLE_CODES = [c.value for c in StyleCode]


@dataclass
class TagMetrics:
    tag: str
    support: int
    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int


@dataclass
class EvalReport:
    model_version: str
    gold_size: int
    exact_match: float
    micro_precision: float
    micro_recall: float
    micro_f1: float
    macro_f1: float
    per_tag: list[TagMetrics]
    by_subset: dict[str, dict[str, float | int]]


def gold_set_path() -> Path:
    return GOLD_SET_PATH


def load_gold_set(path: Path | None = None) -> list[dict]:
    target = path or GOLD_SET_PATH
    if not target.is_file():
        raise FileNotFoundError(f"Gold set not found: {target}")
    items = []
    with target.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1


def evaluate(
    items: list[dict] | None = None,
    classifier: StyleClassifier | None = None,
) -> EvalReport:
    gold = items if items is not None else load_gold_set()
    clf = classifier or StyleClassifier()

    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)
    support = defaultdict(int)
    exact = 0

    subset_tp = defaultdict(int)
    subset_fp = defaultdict(int)
    subset_fn = defaultdict(int)
    subset_n = defaultdict(int)
    subset_exact = defaultdict(int)

    for row in gold:
        gold_tags = set(row.get("gold_tags") or [])
        predicted = {t.tag for t in clf.classify(
            name=row.get("name") or "",
            description=row.get("description"),
            brand=row.get("brand"),
            category=row.get("category"),
            color=row.get("color"),
            locale=row.get("locale"),
        ).tags}

        subset = row.get("subset") or "unknown"
        subset_n[subset] += 1
        if predicted == gold_tags:
            exact += 1
            subset_exact[subset] += 1

        for tag in STYLE_CODES:
            in_gold = tag in gold_tags
            in_pred = tag in predicted
            if in_gold:
                support[tag] += 1
            if in_gold and in_pred:
                tp[tag] += 1
                subset_tp[subset] += 1
            elif in_pred and not in_gold:
                fp[tag] += 1
                subset_fp[subset] += 1
            elif in_gold and not in_pred:
                fn[tag] += 1
                subset_fn[subset] += 1

    per_tag: list[TagMetrics] = []
    f1s: list[float] = []
    for tag in STYLE_CODES:
        p, r, f1 = _prf(tp[tag], fp[tag], fn[tag])
        f1s.append(f1)
        per_tag.append(
            TagMetrics(
                tag=tag,
                support=support[tag],
                precision=round(p, 4),
                recall=round(r, 4),
                f1=round(f1, 4),
                tp=tp[tag],
                fp=fp[tag],
                fn=fn[tag],
            )
        )

    micro_p, micro_r, micro_f1 = _prf(sum(tp.values()), sum(fp.values()), sum(fn.values()))
    by_subset: dict[str, dict[str, float | int]] = {}
    for subset, n in sorted(subset_n.items()):
        p, r, f1 = _prf(subset_tp[subset], subset_fp[subset], subset_fn[subset])
        by_subset[subset] = {
            "n": n,
            "exact_match": round(subset_exact[subset] / n, 4) if n else 0.0,
            "micro_precision": round(p, 4),
            "micro_recall": round(r, 4),
            "micro_f1": round(f1, 4),
        }

    return EvalReport(
        model_version=MODEL_VERSION,
        gold_size=len(gold),
        exact_match=round(exact / len(gold), 4) if gold else 0.0,
        micro_precision=round(micro_p, 4),
        micro_recall=round(micro_r, 4),
        micro_f1=round(micro_f1, 4),
        macro_f1=round(sum(f1s) / len(f1s), 4) if f1s else 0.0,
        per_tag=per_tag,
        by_subset=by_subset,
    )


def report_to_dict(report: EvalReport) -> dict:
    payload = asdict(report)
    payload["per_tag"] = [asdict(t) for t in report.per_tag]
    return payload


def main() -> None:
    report = evaluate()
    print(json.dumps(report_to_dict(report), indent=2))


if __name__ == "__main__":
    main()
