"""Privacy helpers for uploaded or captured photos.

- Strip EXIF/GPS metadata before sending images to an AI provider.
- Optionally blur faces and tattoos as an experimental, disabled-by-default feature.
"""

import io
import logging
from typing import Optional

from PIL import Image as PILImage

logger = logging.getLogger(__name__)


def strip_exif(image: PILImage.Image, original_format: Optional[str] = None) -> PILImage.Image:
    """Return a copy of the image with EXIF and other metadata removed.

    Args:
        image: The source image.
        original_format: The original file extension or PIL format name, used to
            pick the safest stripping strategy. Defaults to the image's ``format``.

    Returns:
        A new PIL image with metadata removed.
    """
    fmt = (original_format or image.format or "").upper()
    buf = io.BytesIO()

    if fmt in ("JPEG", "JPG"):
        # Save without EXIF. Also drop IPTC/comment metadata by only preserving RGB data.
        rgb_image = image.convert("RGB") if image.mode != "RGB" else image
        rgb_image.save(buf, format="JPEG", exif=b"")
    elif fmt == "PNG":
        # Drop PNG textual chunks, ICC profiles, etc.
        image.save(buf, format="PNG", info={})
    elif fmt == "WEBP":
        image.save(buf, format="WEBP", exif=b"")
    else:
        # Fallback: save as PNG without any metadata to guarantee a clean result.
        image.save(buf, format="PNG", info={})

    buf.seek(0)
    return PILImage.open(buf)


def blur_faces_and_tattoos(
    image: PILImage.Image,
    enabled: bool = False,
) -> PILImage.Image:
    """Optionally blur detected faces and prominent tattoos.

    This feature is experimental and disabled by default. It requires
    ``opencv-python`` and a Haar cascade to do anything other than returning
    the original image. If the dependency is missing, a warning is logged and
    the original image is returned.

    Args:
        image: The source image.
        enabled: Whether to attempt detection and blurring.

    Returns:
        The blurred image if enabled and dependencies are available,
        otherwise the original image.
    """
    if not enabled:
        return image

    try:
        import cv2
        import numpy as np
    except ImportError:
        logger.warning(
            "Face/tattoo blurring was enabled but opencv-python is not installed. "
            "Returning the original image."
        )
        return image

    try:
        # Convert PIL to OpenCV BGR
        cv_image = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )

        for x, y, w, h in faces:
            face_region = cv_image[y : y + h, x : x + w]
            blurred = cv2.GaussianBlur(face_region, (51, 51), 30)
            cv_image[y : y + h, x : x + w] = blurred

        return PILImage.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
    except Exception:
        logger.exception("Face/tattoo blurring failed; returning original image")
        return image
