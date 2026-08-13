from app.services.style_classifier import StyleClassifier
from app.services.style_classifier_f1 import (
    DEFAULT_MODEL_PATH,
    StyleClassifierF1,
    StyleClassifierHybrid,
)
from app.services.style_eval import evaluate, load_gold_set


def test_f1_model_artifact_exists():
    assert DEFAULT_MODEL_PATH.is_file()


def test_f1_improves_paraphrase_over_f0():
    gold = load_gold_set()
    f0 = evaluate(gold, classifier=StyleClassifier())
    f1 = evaluate(gold, classifier=StyleClassifierF1())
    assert f1.model_version == "nlp-tfidf-v1"
    assert f1.by_subset["paraphrase"]["micro_f1"] > f0.by_subset["paraphrase"]["micro_f1"]
    assert f1.by_subset["paraphrase"]["micro_f1"] >= 0.50


def test_hybrid_keeps_lexicon_and_precision():
    gold = load_gold_set()
    report = evaluate(gold, classifier=StyleClassifierHybrid())
    assert report.model_version == "hybrid-f0-f1-v1"
    assert report.by_subset["lexicon"]["micro_f1"] >= 0.99
    assert report.micro_precision >= 0.95
    assert report.by_subset["paraphrase"]["micro_f1"] >= 0.50
    assert report.micro_f1 >= f0_micro_floor()


def f0_micro_floor() -> float:
    return evaluate(load_gold_set(), classifier=StyleClassifier()).micro_f1


def test_hybrid_fallback_on_paraphrase_example():
    clf = StyleClassifierHybrid()
    result = clf.classify(
        name="Tuxedo Dinner Jacket",
        description="Peak-lapel tux for black-tie dinners.",
        brand="Atelier Vue",
        category="evening",
        color="black",
    )
    assert result.model_version == "hybrid-f0-f1-v1"
    assert {t.tag for t in result.tags} == {"formal"}
