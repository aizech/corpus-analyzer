"""Model configuration and selection helpers."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

MODEL_OPTIONS: Dict[str, str] = {
    "gpt-4o": "openai:gpt-4o",
    "gpt-4o-mini": "openai:gpt-4o-mini",
    "gpt-5": "openai:gpt-5",
    "gpt-5.2": "openai:gpt-5.2",
    "gpt-5.4-mini": "openai:gpt-5.4-mini",
    "gpt-5.4": "openai:gpt-5.4",
    "gpt-5.5": "openai:gpt-5.5",
}

DEFAULT_MODEL_KEY = "gpt-5.4-mini"


def _config_path() -> str:
    """Return the path to model_config.json in the project root."""
    return str(Path(__file__).parent / "model_config.json")


def ensure_model_config() -> Dict[str, str]:
    """Ensure a model_config.json exists and return its contents."""
    config_path = _config_path()
    default_config = {"default_model": DEFAULT_MODEL_KEY}

    if not os.path.exists(config_path):
        save_model_config(default_config)
        return default_config

    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        config = default_config
        save_model_config(config)

    if "default_model" not in config or config["default_model"] not in MODEL_OPTIONS:
        config["default_model"] = DEFAULT_MODEL_KEY
        save_model_config(config)

    return config


def get_default_model_key() -> str:
    """Return the configured default model key."""
    config = ensure_model_config()
    return config.get("default_model", DEFAULT_MODEL_KEY)


def get_default_model_id() -> str:
    """Return the full OpenAI model ID for the configured default model."""
    key = get_default_model_key()
    return MODEL_OPTIONS.get(key, MODEL_OPTIONS[DEFAULT_MODEL_KEY])


def set_default_model(key: str) -> None:
    """Persist the default model key."""
    if key not in MODEL_OPTIONS:
        raise ValueError(f"Unknown model key: {key}")
    save_model_config({"default_model": key})


def save_model_config(config: Dict[str, str]) -> None:
    """Save the model configuration to disk."""
    config_path = _config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_model_id(key: Optional[str] = None) -> str:
    """Return the OpenAI model ID for a given key or the default."""
    if key is None:
        return get_default_model_id()
    if key not in MODEL_OPTIONS:
        raise ValueError(f"Unknown model key: {key}")
    return MODEL_OPTIONS[key]
