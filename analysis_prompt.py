"""Build the analysis prompt sent to the routed medical imaging agent.

This module is intentionally free of Streamlit dependencies so it can be
imported and unit-tested without a running Streamlit script context.
"""

from typing import Dict, List, Optional

ROLE_INSTRUCTIONS: Dict[str, str] = {
    "clinician": (
        "You are writing for a qualified healthcare professional. "
        "Use precise terminology, structured findings, and keep the tone concise and clinical."
    ),
    "patient": (
        "You are explaining the results to a patient with no medical background. "
        "Use plain language, avoid jargon, and focus on what the findings mean and what to do next."
    ),
    "researcher": (
        "You are writing for a medical researcher. Include technical detail, differential considerations, "
        "confidence discussion, and evidence-based references where possible."
    ),
}

LANGUAGE_INSTRUCTIONS: Dict[str, str] = {
    "de": "Answer in German.",
    "en": "Answer in English.",
}

ANAMNESIS_KEY_LABELS: Dict[str, str] = {
    "since_when": "Since when",
    "has_changed": "Has it changed",
    "itching": "Itching",
    "bleeding": "Bleeding",
    "pain": "Pain",
    "size_approx": "Approximate size",
    "additional_notes": "Additional notes",
}


def build_anamnesis_text(
    anamnesis: Optional[Dict[str, str]],
    label: str = "Anamnesis",
    labels: Optional[Dict[str, str]] = None,
) -> str:
    """Build a short anamnesis paragraph from a dictionary of user answers.

    Args:
        anamnesis: Mapping of anamnesis keys to user-provided strings.
        label: Heading label for the anamnesis section.
        labels: Optional mapping of anamnesis keys to display labels. Defaults
            to English labels.

    Returns:
        A formatted anamnesis block, or an empty string if no answers were given.
    """
    if not anamnesis:
        return ""

    label_map = labels if labels is not None else ANAMNESIS_KEY_LABELS
    parts: List[str] = []
    for key, heading in label_map.items():
        value = anamnesis.get(key)
        if value:
            parts.append(f"- {heading}: {value}")

    if not parts:
        return ""
    return f"{label}:\n" + "\n".join(parts)


def build_analysis_prompt(
    additional_info: str,
    role: str,
    language: str,
    anamnesis_text: str = "",
) -> str:
    """Build the prompt sent to the medical imaging agent.

    Args:
        additional_info: Extra context or quick-prompt instructions.
        role: Target audience role ("clinician", "patient", or "researcher").
        language: Response language code ("en" or "de").
        anamnesis_text: Optional pre-formatted anamnesis block.

    Returns:
        The complete prompt string for the agent.
    """
    role_instruction = ROLE_INSTRUCTIONS.get(role, "")
    language_instruction = LANGUAGE_INSTRUCTIONS.get(
        language,
        "Answer in the language of the user; if not specified, answer in English.",
    )

    base_parts: List[str] = []
    if additional_info:
        base_parts.append(
            "Analyze the provided image(s) considering the following context: " + additional_info
        )
    else:
        base_parts.append("Analyze the provided image(s) and provide detailed findings.")

    if anamnesis_text:
        base_parts.append(anamnesis_text)

    base = "\n\n".join(base_parts)

    return (
        f"Role: {role.capitalize()}\n\n"
        f"{role_instruction}\n\n"
        f"{base}\n\n"
        "If you are not sure about what you see, please say so rather than guessing. "
        "If the image quality or content is insufficient for assessment, state explicitly "
        "that you cannot assess it and explain what is missing or how to improve the image(s). "
        f"{language_instruction}"
    )
