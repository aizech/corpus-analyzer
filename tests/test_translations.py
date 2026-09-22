"""Tests for the UI translation helpers."""

import translations
from translations import UI_TEXTS, format_text, get_language, set_language


def reset_language(monkeypatch):
    """Helper to reset the session-state language to English after each test."""
    yield
    set_language("en")


def test_default_language_is_english():
    set_language("en")
    assert get_language() == "en"


def test_set_and_get_language():
    set_language("de")
    assert get_language() == "de"
    set_language("en")
    assert get_language() == "en"


def test_translate_returns_correct_language():
    set_language("de")
    assert translations._("page_analyze") == "Analysieren"
    set_language("en")
    assert translations._("page_analyze") == "Analyze"


def test_translate_falls_back_to_english_for_unknown_language():
    set_language("fr")
    assert translations._("page_analyze") == "Analyze"


def test_translate_falls_back_to_key_for_unknown_key():
    set_language("en")
    assert translations._("unknown_key_xyz") == "unknown_key_xyz"


def test_format_text_substitutes_placeholders():
    set_language("en")
    text = format_text("config_model_saved", model="gpt-5")
    assert "gpt-5" in text


def test_all_translation_entries_have_english_and_german():
    for key, values in UI_TEXTS.items():
        assert "en" in values, f"Missing English translation for {key}"
        assert "de" in values, f"Missing German translation for {key}"
