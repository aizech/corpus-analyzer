"""Tests for model configuration helpers."""

import pytest

from models import (
    DEFAULT_MODEL_KEY,
    MODEL_OPTIONS,
    ensure_model_config,
    get_default_model_id,
    get_default_model_key,
    get_model_id,
    set_default_model,
)


def test_model_options_contains_expected_keys():
    assert "gpt-5.4-mini" in MODEL_OPTIONS
    assert "gpt-4o" in MODEL_OPTIONS
    assert MODEL_OPTIONS["gpt-5.4-mini"] == "openai:gpt-5.4-mini"


def test_ensure_model_config_creates_default(tmp_path, monkeypatch):
    config_file = tmp_path / "model_config.json"
    monkeypatch.setattr("models._config_path", lambda: str(config_file))

    config = ensure_model_config()
    assert config["default_model"] == DEFAULT_MODEL_KEY
    assert config_file.exists()


def test_set_and_get_default_model(tmp_path, monkeypatch):
    config_file = tmp_path / "model_config.json"
    monkeypatch.setattr("models._config_path", lambda: str(config_file))

    set_default_model("gpt-4o")
    assert get_default_model_key() == "gpt-4o"
    assert get_default_model_id() == "openai:gpt-4o"


def test_get_model_id_unknown_key_raises():
    with pytest.raises(ValueError):
        get_model_id("unknown-model")
