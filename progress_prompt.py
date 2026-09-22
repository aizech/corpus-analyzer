"""Build comparison prompts for progress-tracking snapshots.

The prompts are intentionally educational and avoid diagnosis, triage, or
urgency classification.
"""

from typing import List

from storage.models import PhotoSnapshot


def _format_snapshot(snapshot: PhotoSnapshot) -> str:
    lines: List[str] = []
    lines.append(f"Date: {snapshot.created_at.isoformat()}")
    if snapshot.body_site:
        lines.append(f"Body site: {snapshot.body_site}")
    if snapshot.anamnesis:
        lines.append(f"Anamnesis:\n{snapshot.anamnesis}")
    if snapshot.analysis_summary:
        lines.append(f"Previous summary:\n{snapshot.analysis_summary}")
    return "\n".join(lines)


def build_comparison_prompt(
    earlier: PhotoSnapshot,
    later: PhotoSnapshot,
    role: str = "patient",
    language: str = "en",
) -> str:
    """Build a prompt that asks the model to compare two snapshots.

    Args:
        earlier: The older snapshot.
        later: The newer snapshot.
        role: Target audience (clinician / patient / researcher).
        language: Response language code.

    Returns:
        A prompt string for the routed agent.
    """
    role_instruction = {
        "clinician": (
            "You are writing for a qualified healthcare professional. "
            "Be concise, use precise terminology, and focus on observable changes."
        ),
        "patient": (
            "You are explaining the comparison to a patient with no medical background. "
            "Use plain language, avoid jargon, and focus on what looks different and what to do next."
        ),
        "researcher": (
            "You are writing for a medical researcher. Discuss observable changes, "
            "technical considerations, and evidence-based context where possible."
        ),
    }.get(role, "")

    language_instruction = {"de": "Answer in German.", "en": "Answer in English."}.get(
        language,
        "Answer in the language of the user; if not specified, answer in English.",
    )

    return (
        f"Role: {role.capitalize()}\n\n"
        f"{role_instruction}\n\n"
        "Compare the two photographs of the same body area taken at different times. "
        "Describe observable changes using the ABCDE framework as observations only: "
        "A = asymmetry, B = border, C = color, D = diameter/size, E = evolution over time. "
        "If a photo is unsuitable, say so. Do not diagnose. Do not classify urgency. "
        "At the end, suggest conservatively whether seeing a doctor could be useful and why.\n\n"
        f"--- Snapshot 1 (earlier, {earlier.created_at.isoformat()}) ---\n"
        f"{_format_snapshot(earlier)}\n\n"
        f"--- Snapshot 2 (later, {later.created_at.isoformat()}) ---\n"
        f"{_format_snapshot(later)}\n\n"
        f"{language_instruction}"
    )
