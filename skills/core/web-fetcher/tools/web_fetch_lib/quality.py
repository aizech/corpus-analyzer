"""Quality heuristics used to decide whether to try the next fetch engine."""

import re

from web_fetch_lib.schemas import FetchResult

_MIN_CONTENT_CHARS = 200
_HEADING_RE = re.compile(r"(?m)^(#{1,6} .+)$")
_BOILERPLATE_RE = re.compile(
    r"\b(sign in|log in|sign up|subscribe|newsletter|cookie policy|privacy policy|terms of use|"
    r"all rights reserved|copyright \u00a9|site map|navigation|footer|header|sidebar)\b",
    re.IGNORECASE,
)


def heading_count(markdown: str) -> int:
    return len(_HEADING_RE.findall(markdown))


def boilerplate_score(markdown: str) -> float:
    """Ratio of boilerplate keyword occurrences per 1,000 characters."""
    text = markdown.lower()
    if not text:
        return 0.0
    matches = len(_BOILERPLATE_RE.findall(text))
    return matches / (len(text) / 1000.0)


def is_low_quality(result: FetchResult) -> bool:
    """Return True if the result is likely incomplete or noisy."""
    if not result or not result.markdown:
        return True
    text = result.markdown.strip()
    if len(text) < _MIN_CONTENT_CHARS:
        return True
    if result.render_path in {"pdf", "manual"}:
        return False
    return heading_count(text) == 0 and len(text) < _MIN_CONTENT_CHARS * 3


def quality_summary(result: FetchResult) -> dict:
    """Return a dictionary of quality metrics for logging/benchmarking."""
    text = (result.markdown or "").strip()
    return {
        "chars": len(text),
        "headings": heading_count(text),
        "boilerplate_score": boilerplate_score(text),
        "low_quality": is_low_quality(result),
    }
