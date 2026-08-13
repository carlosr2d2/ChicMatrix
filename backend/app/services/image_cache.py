"""Download and serve scraped product images from local disk cache."""

from __future__ import annotations

import logging
import mimetypes
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.models.models import Product

logger = logging.getLogger(__name__)

_SAFE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


def media_root() -> Path:
    env = os.getenv("MEDIA_ROOT") or settings.media_root
    path = Path(env)
    path.mkdir(parents=True, exist_ok=True)
    (path / "products").mkdir(parents=True, exist_ok=True)
    return path


def public_media_path(relative: str) -> str:
    """Browser-facing absolute URL for a cached media file."""
    rel = relative if relative.startswith("/") else f"/{relative}"
    return f"{settings.api_base_url.rstrip('/')}{rel}"


def absolute_image_url(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return f"{settings.api_base_url.rstrip('/')}{url}"
    return url


def _extension_from_url_and_type(url: str, content_type: str | None) -> str:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix in _SAFE_EXT:
        return ".jpg" if suffix == ".jpeg" else suffix
    if content_type:
        guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if guessed == ".jpe":
            guessed = ".jpg"
        if guessed and guessed.lower() in _SAFE_EXT:
            return guessed.lower()
    return ".jpg"


def _is_remote_http(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _already_cached(url: str | None) -> bool:
    if not url:
        return False
    return "/media/products/" in url


def cache_product_image(
    product: Product,
    *,
    source_url: str | None = None,
    headers: dict | None = None,
) -> str | None:
    """
    Download remote product image to MEDIA_ROOT/products/{id}{ext}.

    Stores original remote URL in product.image_source_url and sets
    product.image_url to a public /media/... path (relative).
    Returns the relative media path on success, else None.
    """
    remote = source_url or product.image_source_url or product.image_url
    if not remote or not _is_remote_http(remote):
        return None
    if _already_cached(product.image_url) and product.image_source_url:
        # Refresh only if source changed.
        if product.image_source_url == remote:
            return product.image_url

    req_headers = headers or {"User-Agent": "ChicMatrixBot/1.0 (+image-cache)"}
    try:
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(remote, headers=req_headers)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if content_type and not content_type.startswith("image/"):
                logger.warning(
                    "Skipping non-image cache",
                    extra={"product_id": product.id, "content_type": content_type},
                )
                return None
            ext = _extension_from_url_and_type(remote, content_type)
            data = response.content
            if not data:
                return None
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Image cache download failed",
            extra={"product_id": product.id, "url": remote, "error": str(exc)},
        )
        return None

    safe_id = re.sub(r"[^0-9A-Za-z_-]", "_", str(product.id))
    relative = f"/media/products/{safe_id}{ext}"
    dest = media_root() / "products" / f"{safe_id}{ext}"
    # Remove previous extensions for this product id.
    for old in (media_root() / "products").glob(f"{safe_id}.*"):
        if old != dest:
            try:
                old.unlink()
            except OSError:
                pass
    dest.write_bytes(data)

    product.image_source_url = remote
    product.image_url = relative
    logger.info(
        "Cached product image",
        extra={"product_id": product.id, "bytes": len(data), "path": relative},
    )
    return relative
