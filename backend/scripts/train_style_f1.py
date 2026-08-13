"""Train and evaluate F1 TF-IDF style classifier against the gold set."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow `python scripts/train_style_f1.py` from backend/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.style_classifier import StyleClassifier
from app.services.style_classifier_f1 import (
    DEFAULT_MODEL_PATH,
    DEFAULT_THRESHOLD,
    StyleClassifierF1,
    StyleClassifierHybrid,
    save_model,
    train_tfidf_model,
)
from app.services.style_eval import evaluate, load_gold_set, report_to_dict


def main() -> None:
    parser = argparse.ArgumentParser(description="Train F1 style classifier")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Path to write production model JSON",
    )
    parser.add_argument(
        "--baseline-out",
        type=Path,
        default=ROOT / "fixtures" / "style_gold" / "f1_baseline.json",
    )
    args = parser.parse_args()

    gold = load_gold_set()
    train_all = gold
    holdout_train = [r for r in gold if (r.get("subset") or "") != "paraphrase"]
    paraphrase = [r for r in gold if (r.get("subset") or "") == "paraphrase"]

    prod_model = train_tfidf_model(train_all, threshold=args.threshold)
    path = save_model(prod_model, args.out)

    holdout_model = train_tfidf_model(holdout_train, threshold=args.threshold)

    f0 = StyleClassifier()
    f1 = StyleClassifierF1(model=prod_model)
    hybrid = StyleClassifierHybrid(f0=f0, f1=f1)
    holdout_hybrid = StyleClassifierHybrid(
        f0=f0,
        f1=StyleClassifierF1(model=holdout_model),
    )

    reports = {
        "f0": report_to_dict(evaluate(gold, classifier=f0)),
        "f1": report_to_dict(evaluate(gold, classifier=f1)),
        "hybrid": report_to_dict(evaluate(gold, classifier=hybrid)),
        "hybrid_holdout_paraphrase": report_to_dict(
            evaluate(paraphrase, classifier=holdout_hybrid)
        ),
    }

    payload = {
        "model_path": str(path.as_posix()),
        "threshold": args.threshold,
        "train_size": prod_model.train_size,
        "train_subsets": prod_model.train_subsets,
        "notes": {
            "hybrid": "F0-first; F1 only when F0 returns no tags",
            "hybrid_holdout_paraphrase": (
                "Honest paraphrase generalization: F1 trained without paraphrase subset"
            ),
        },
        "reports": reports,
    }
    args.baseline_out.parent.mkdir(parents=True, exist_ok=True)
    args.baseline_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nSaved model -> {path}")
    print(f"Saved baseline -> {args.baseline_out}")


if __name__ == "__main__":
    main()
