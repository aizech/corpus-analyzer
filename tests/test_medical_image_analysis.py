"""Tests for the analysis view helpers (prompt builder only)."""

from analysis_prompt import build_analysis_prompt, build_anamnesis_text


def test_build_anamnesis_text_returns_empty_without_data():
    assert build_anamnesis_text({}) == ""
    assert build_anamnesis_text(None) == ""


def test_build_anamnesis_text_includes_answered_fields():
    anamnesis = {
        "since_when": "3 days",
        "itching": "yes",
        "pain": "mild",
        "bleeding": "",
        "has_changed": "",
        "size_approx": "",
        "additional_notes": "grew after sun exposure",
    }
    text = build_anamnesis_text(anamnesis)
    assert "Since when: 3 days" in text
    assert "Itching: yes" in text
    assert "Pain: mild" in text
    assert "Additional notes: grew after sun exposure" in text
    assert "Bleeding" not in text
    assert "Has it changed" not in text


def test_build_anamnesis_text_uses_custom_labels():
    anamnesis = {"since_when": "1 week"}
    labels = {"since_when": "Seit wann"}
    text = build_anamnesis_text(anamnesis, label="Anamnese", labels=labels)
    assert "Anamnese:" in text
    assert "Seit wann: 1 week" in text


def test_build_analysis_prompt_contains_role_and_language():
    prompt = build_analysis_prompt(
        additional_info="context here",
        role="patient",
        language="de",
    )
    assert "Role: Patient" in prompt
    assert "no medical background" in prompt
    assert "Answer in German." in prompt


def test_build_analysis_prompt_includes_additional_info():
    prompt = build_analysis_prompt(
        additional_info="Focus on red flags.",
        role="clinician",
        language="en",
    )
    assert "Analyze the provided image(s) considering the following context:" in prompt
    assert "Focus on red flags." in prompt


def test_build_analysis_prompt_includes_anamnesis():
    anamnesis_text = build_anamnesis_text({"itching": "yes", "pain": "no"})
    prompt = build_analysis_prompt(
        additional_info="",
        role="researcher",
        language="en",
        anamnesis_text=anamnesis_text,
    )
    assert "Itching: yes" in prompt
    assert "Pain: no" in prompt
    assert "medical researcher" in prompt


def test_build_analysis_prompt_requests_uncertainty_language():
    prompt = build_analysis_prompt(
        additional_info="",
        role="patient",
        language="de",
    )
    assert "If you are not sure about what you see, please say so rather than guessing" in prompt
    assert "I cannot assess it" not in prompt  # phrasing is in the instruction
