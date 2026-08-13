from pathlib import Path

from app.models.enums import StyleCode
from app.services.style_eval import evaluate, gold_set_path, load_gold_set, report_to_dict


def test_gold_set_size_and_coverage():
    items = load_gold_set()
    assert 300 <= len(items) <= 500
    tags_seen: set[str] = set()
    subsets: set[str] = set()
    for row in items:
        assert "id" in row and "name" in row
        assert isinstance(row["gold_tags"], list)
        tags_seen.update(row["gold_tags"])
        subsets.add(row["subset"])
    assert tags_seen == {c.value for c in StyleCode}
    assert {"lexicon", "paraphrase", "overlap", "negative"} <= subsets
    assert gold_set_path().is_file()


def test_f0_eval_lexicon_stronger_than_paraphrase():
    report = evaluate()
    assert report.gold_size >= 300
    assert report.model_version == "rules-v1"
    assert report.by_subset["lexicon"]["micro_f1"] >= 0.85
    assert report.by_subset["lexicon"]["micro_f1"] > report.by_subset["paraphrase"]["micro_f1"]
    assert report.micro_f1 >= 0.55
    assert report.macro_f1 >= 0.50
    for tag_row in report.per_tag:
        assert tag_row.support > 0


def test_report_to_dict_serializable():
    payload = report_to_dict(evaluate())
    assert payload["gold_size"] == evaluate().gold_size
    assert isinstance(payload["per_tag"], list)
    assert Path(gold_set_path()).name == "gold_set.jsonl"
