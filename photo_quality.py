"""Lightweight photo-quality checks for smartphone health photos.

This module uses only Pillow and NumPy (already required by the project) so it
does not add an extra dependency. The checks are intentionally simple heuristics:
they give users guidance, not a pass/fail verdict, and they do not block
analysis.
"""

from typing import Dict, List

import numpy as np
from PIL import Image as PILImage


def _laplacian_variance(gray: np.ndarray) -> float:
    """Approximate Laplacian variance as a blur metric.

    A higher value usually means a sharper image. The threshold used by callers
    is intentionally conservative.
    """
    # Compute second derivative approximations with simple kernels.
    dx = np.diff(gray.astype(np.float32), axis=1, append=gray[:, -1:])
    dy = np.diff(gray.astype(np.float32), axis=0, append=gray[-1:, :])
    dxx = np.diff(dx, axis=1, append=dx[:, -1:])
    dyy = np.diff(dy, axis=0, append=dy[-1:, :])
    laplacian = dxx + dyy
    return float(np.var(laplacian))


def assess_image_quality(image: PILImage.Image) -> Dict[str, object]:
    """Return basic quality metrics and guidance flags for a photo.

    Args:
        image: A PIL Image.

    Returns:
        A dictionary with:
        - ``blur_score``: float (higher is sharper)
        - ``brightness``: float (0-255 mean grayscale value)
        - ``contrast``: float (standard deviation of grayscale)
        - ``warnings``: list of string flags such as "too_dark",
          "too_bright", "too_blurry", "low_contrast"
    """
    gray = np.array(image.convert("L"))

    blur_score = _laplacian_variance(gray)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))

    warnings: List[str] = []
    if brightness < 50:
        warnings.append("too_dark")
    if brightness > 220:
        warnings.append("too_bright")
    if contrast < 25:
        warnings.append("low_contrast")
    # Conservative blur threshold for smartphone close-up photos.
    if blur_score < 80:
        warnings.append("too_blurry")

    return {
        "blur_score": blur_score,
        "brightness": brightness,
        "contrast": contrast,
        "warnings": warnings,
    }


def quality_warning_text(warnings: List[str], language: str = "en") -> str:
    """Return a human-readable warning string for the given warning flags."""
    messages: Dict[str, Dict[str, str]] = {
        "too_dark": {
            "en": "The photo looks dark. Good lighting helps the analysis.",
            "de": "Das Foto wirkt dunkel. Gutes Licht hilft der Analyse.",
        },
        "too_bright": {
            "en": "The photo looks very bright or overexposed.",
            "de": "Das Foto wirkt sehr hell oder überbelichtet.",
        },
        "low_contrast": {
            "en": "The photo has low contrast. Details may be hard to see.",
            "de": "Das Foto hat wenig Kontrast. Details sind schwer zu erkennen.",
        },
        "too_blurry": {
            "en": "The photo looks blurry. A sharper image improves the analysis.",
            "de": "Das Foto wirkt unscharf. Ein schärferes Bild verbessert die Analyse.",
        },
    }
    parts = [messages[w][language] for w in warnings if w in messages]
    if not parts:
        return ""
    return " ".join(parts)


def is_quality_assessment_available() -> bool:
    """Return True because Pillow and NumPy are already required."""
    return True
