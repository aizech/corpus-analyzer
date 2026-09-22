"""Build PhotoSnapshot instances from an analysis session."""

import hashlib
import re
from typing import Dict, List, Optional

from storage.models import PhotoSnapshot, SnapshotTag

_TAG_KEYWORDS: Dict[SnapshotTag, List[str]] = {
    SnapshotTag.SKIN: ["skin", "mole", "melanoma", "pigment", "dermat", "haut", "leberfleck"],
    SnapshotTag.NAIL: ["nail", "toenail", "fingernail", "nagel"],
    SnapshotTag.WOUND: ["wound", "injury", "cut", "abrasion", "wunde", "verletzung"],
    SnapshotTag.RASH: ["rash", "erythema", "exanthem", "ausschlag", "hautausschlag"],
    SnapshotTag.DOCUMENT: [
        "document",
        "letter",
        "lab report",
        "medication",
        "brief",
        "labor",
        "medikament",
    ],
}


def _detect_tags(prompt: str, analysis_text: str) -> List[SnapshotTag]:
    """Detect likely snapshot tags from prompt and analysis text."""
    combined = (prompt or "") + " " + (analysis_text or "")
    lowered = combined.lower()
    tags: List[SnapshotTag] = []
    for tag, keywords in _TAG_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(keyword)}\b", lowered) for keyword in keywords):
            tags.append(tag)
    if not tags:
        tags.append(SnapshotTag.OTHER)
    return tags


def _first_paragraph(text: str, max_chars: int = 500) -> str:
    """Return the first paragraph or up to max_chars of the analysis."""
    if not text:
        return ""
    paragraph = text.split("\n\n")[0].strip()
    if len(paragraph) > max_chars:
        paragraph = paragraph[:max_chars].rsplit(" ", 1)[0] + "..."
    return paragraph


def build_snapshot(
    user_id: str,
    images: List[Dict[str, object]],
    body_site: Optional[str],
    anamnesis: Dict[str, str],
    analysis_text: str,
    role: str,
    prompt: str,
) -> PhotoSnapshot:
    """Create a PhotoSnapshot from the current analysis session.

    Args:
        user_id: Stable identifier for the user/session.
        images: Session gallery items with ``bytes`` keys.
        body_site: Selected body location, if any.
        anamnesis: Dictionary of anamnesis answers.
        analysis_text: Full analysis text produced by the agent.
        role: Role the analysis was generated for (clinician/patient/researcher).
        prompt: Prompt text sent to the agent.

    Returns:
        A ``PhotoSnapshot`` ready to be persisted by a storage backend.
    """
    if not images:
        raise ValueError("At least one image is required to build a snapshot")

    first_image_bytes = images[0]["bytes"]
    image_hash = hashlib.sha256(first_image_bytes).hexdigest()

    anamnesis_lines = [f"{key}: {value}" for key, value in anamnesis.items() if value]
    anamnesis_text = "\n".join(anamnesis_lines) if anamnesis_lines else None

    summary = _first_paragraph(analysis_text)

    tags = _detect_tags(prompt, analysis_text)

    return PhotoSnapshot.create(
        user_id=user_id,
        image_hash=image_hash,
        body_site=body_site,
        anamnesis=anamnesis_text,
        analysis_summary=summary,
        encrypted_image=first_image_bytes,
        tags=tags,
        metadata={"role": role, "image_count": str(len(images))},
    )
