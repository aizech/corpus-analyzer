"""Tests for the body map selector helpers."""

from ui.body_map import BODY_SITE_OPTIONS, body_site_label


def test_body_site_options_are_hierarchical_strings():
    for key in BODY_SITE_OPTIONS:
        assert ":" in key or key == "other"


def test_body_site_label_returns_translation_key():
    assert body_site_label("front:chest")  # Should return a non-empty string


def test_body_site_label_fallback_for_unknown():
    assert body_site_label("unknown:site") == "unknown:site"
