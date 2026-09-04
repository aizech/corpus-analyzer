"""Parse structured medical image analysis responses into sections."""

import re
from typing import Dict, Optional

SECTION_PATTERN = re.compile(
    r"^(?:###|##)\s+(?:\d+\.\s+)?(?P<title>[^\n]+)\n(?P<body>(?:.*\n?)*?)(?=(?:\n(?:###|##)\s+(?:\d+\.\s+)?)|\Z)",
    re.MULTILINE,
)


SECTION_TITLES: Dict[str, str] = {
    "image technical assessment": "Image Technical Assessment",
    "professional analysis": "Professional Analysis",
    "clinical interpretation": "Clinical Interpretation",
    "patient education": "Patient Education",
    "evidence-based context": "Evidence-Based Context",
    "medical disclaimer": "Medical Disclaimer",
}


def parse_analysis_sections(text: str) -> Dict[str, str]:
    """Split an analysis markdown response into labeled sections.

    Args:
        text: The raw markdown response from the medical imaging agent.

    Returns:
        A dict mapping lowercase section titles to their markdown content.
        If no sections are detected, the full text is returned under the
        key ``_raw``.
    """
    sections: Dict[str, str] = {}
    for match in SECTION_PATTERN.finditer(text):
        title = match.group("title").strip().lower().rstrip(":")
        body = match.group("body").strip()
        sections[title] = body

    if not sections:
        sections["_raw"] = text.strip()

    return sections


def confidence_level(text: str) -> Optional[str]:
    """Infer a confidence level from the analysis text.

    Args:
        text: The analysis text to scan.

    Returns:
        One of ``high``, ``medium``, ``low``, or ``uncertain`` if detected,
        otherwise ``None``.
    """
    lowered = text.lower()
    if re.search(r"\bhigh confidence\b|\bhigh\s+probability\b", lowered):
        return "high"
    if re.search(
        r"\bmedium confidence\b|\bmoderate confidence\b|\bmedium\s+probability\b", lowered
    ):
        return "medium"
    if re.search(r"\blow confidence\b|\blow\s+probability\b", lowered):
        return "low"
    if re.search(r"\buncertain\b|\bunknown\b|\bcannot determine\b", lowered):
        return "uncertain"
    return None
