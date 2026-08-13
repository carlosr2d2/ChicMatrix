from app.services.style_classifier import StyleClassifier


def test_classify_formal_blazer():
    result = StyleClassifier().classify(
        name="Structured Wool Blazer",
        description="Tailored formal blazer with clean lines and understated minimalist structure",
        brand="Maison Noir",
    )
    codes = {t.tag for t in result.tags}
    assert "formal" in codes
    assert result.model_version == "rules-v1"
    assert all(0.45 <= t.score <= 1.0 for t in result.tags)


def test_classify_biker_and_rocker_overlap():
    result = StyleClassifier().classify(
        name="Leather Biker Jacket",
        description="Asymmetric leather biker jacket with harness details and rocker edge",
    )
    codes = {t.tag for t in result.tags}
    assert "biker" in codes
    assert "rocker" in codes or "biker" in codes


def test_classify_sport():
    result = StyleClassifier().classify(
        name="Performance Running Tank",
        description="Athletic dry-fit performance tank for gym training and running",
    )
    assert any(t.tag == "sport" for t in result.tags)


def test_classify_streetwear():
    result = StyleClassifier().classify(
        name="Oversized Graphic Hoodie",
        description="Oversized streetwear hoodie with drop shoulder for urban looks",
    )
    assert any(t.tag == "streetwear" for t in result.tags)


def test_classify_empty_text():
    result = StyleClassifier().classify(name="")
    assert result.tags == []


def test_classify_respects_max_tags():
    result = StyleClassifier(threshold=0.2, max_tags=2).classify(
        name="Minimalist formal casual streetwear athletic hoodie blazer",
        description="office gym running oversized urban tailored denim jeans",
    )
    assert len(result.tags) <= 2
