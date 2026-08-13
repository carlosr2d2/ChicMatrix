"""Resolve active style classifier (F0 / F1 / hybrid)."""

from __future__ import annotations

from app.config import settings
from app.services.style_classifier import StyleClassifier
from app.services.style_classifier_f1 import StyleClassifierF1, StyleClassifierHybrid


def get_style_classifier():
    """Return classifier based on STYLE_CLASSIFIER_MODE env/setting."""
    mode = (settings.style_classifier_mode or "hybrid").strip().lower()
    if mode == "f0":
        return StyleClassifier()
    if mode == "f1":
        return StyleClassifierF1()
    if mode == "hybrid":
        return StyleClassifierHybrid()
    raise ValueError(f"Unknown style_classifier_mode: {mode}")
