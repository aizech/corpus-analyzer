"""Tests for the medical imaging agent factory."""

from agents.medical_agent import PROMPT_PATH, create_medical_imaging_agent


def test_prompt_file_exists():
    assert PROMPT_PATH.exists()
    assert PROMPT_PATH.read_text(encoding="utf-8")


def test_create_medical_imaging_agent():
    agent = create_medical_imaging_agent(model_id="openai:gpt-5.4-mini")
    assert agent.name == "Medical Imaging and Search Expert"
