"""Tests for disk-backed product image cache."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.models.models import Product, Retailer
from app.services import image_cache
from app.services.image_cache import absolute_image_url, cache_product_image


@pytest.fixture()
def media_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("MEDIA_ROOT", str(tmp_path))
    monkeypatch.setattr(image_cache.settings, "media_root", str(tmp_path))
    return tmp_path


def _product(db_session, remote: str = "https://cdn.example/pic.jpg") -> Product:
    retailer = Retailer(
        name="Cache Shop",
        base_url="https://cache.demo",
        scraping_config={},
        is_active=True,
    )
    db_session.add(retailer)
    db_session.flush()
    product = Product(
        retailer_id=retailer.id,
        external_id="c-1",
        name="Cached Tee",
        image_url=remote,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def test_absolute_image_url_prefixes_local_media():
    assert absolute_image_url(None) is None
    assert absolute_image_url("https://x/y.jpg") == "https://x/y.jpg"
    abs_url = absolute_image_url("/media/products/9.jpg")
    assert abs_url.endswith("/media/products/9.jpg")
    assert abs_url.startswith("http")


def test_cache_product_image_writes_file_and_rewrites_url(db_session, media_tmp):
    product = _product(db_session)
    fake = MagicMock()
    fake.get.return_value.status_code = 200
    fake.get.return_value.headers = {"content-type": "image/jpeg"}
    fake.get.return_value.content = b"\xff\xd8\xfffakejpeg"
    fake.get.return_value.raise_for_status = MagicMock()
    fake.__enter__.return_value = fake
    fake.__exit__.return_value = False

    with patch("app.services.image_cache.httpx.Client", return_value=fake):
        relative = cache_product_image(product, source_url=product.image_url)

    assert relative == f"/media/products/{product.id}.jpg"
    assert product.image_url == relative
    assert product.image_source_url == "https://cdn.example/pic.jpg"
    assert (media_tmp / "products" / f"{product.id}.jpg").read_bytes().startswith(b"\xff\xd8")


def test_cache_product_image_skips_when_unchanged(db_session, media_tmp):
    product = _product(db_session)
    product.image_url = f"/media/products/{product.id}.jpg"
    product.image_source_url = "https://cdn.example/pic.jpg"
    db_session.commit()

    with patch("app.services.image_cache.httpx.Client") as client_cls:
        result = cache_product_image(product, source_url=product.image_source_url)
        client_cls.assert_not_called()

    assert result == product.image_url


def test_cache_product_image_rejects_non_image(db_session, media_tmp):
    product = _product(db_session)
    fake = MagicMock()
    fake.get.return_value.status_code = 200
    fake.get.return_value.headers = {"content-type": "text/html"}
    fake.get.return_value.content = b"<html></html>"
    fake.get.return_value.raise_for_status = MagicMock()
    fake.__enter__.return_value = fake
    fake.__exit__.return_value = False

    with patch("app.services.image_cache.httpx.Client", return_value=fake):
        assert cache_product_image(product) is None
    assert product.image_url.startswith("https://")
