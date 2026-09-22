"""Tests for photo privacy helpers."""

import io

from PIL import Image as PILImage

from photo_privacy import blur_faces_and_tattoos, is_opencv_available, strip_exif


def _make_jpeg_with_gps() -> bytes:
    """Create a JPEG with GPS EXIF data."""
    img = PILImage.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()

    exif = PILImage.Exif()
    # GPSInfo tag (34853) holds a dict of GPS tags.
    # Pillow converts float values to rational numbers when saving JPEG EXIF.
    exif[34853] = {
        1: "N",  # GPSLatitudeRef
        2: (52.0, 30.0, 0.0),  # GPSLatitude
        3: "E",  # GPSLongitudeRef
        4: (13.0, 24.0, 0.0),  # GPSLongitude
    }
    exif[271] = "TestMaker"  # Make

    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


def test_strip_exif_removes_gps_data():
    raw_bytes = _make_jpeg_with_gps()
    image = PILImage.open(io.BytesIO(raw_bytes))

    # Verify GPS info exists before stripping.
    exif_before = image.getexif()
    assert exif_before is not None
    gps_before = exif_before.get(34853)  # GPSInfo tag
    assert gps_before is not None

    stripped = strip_exif(image, original_format="JPEG")
    exif_after = stripped.getexif()

    if exif_after is not None:
        assert exif_after.get(34853) is None
        assert exif_after.get(271) is None  # Make tag


def test_strip_exif_png_removes_info():
    buf = io.BytesIO()
    PILImage.new("RGBA", (50, 50), color=(255, 0, 0, 128)).save(
        buf, format="PNG", info={"Comment": "private"}
    )
    image = PILImage.open(io.BytesIO(buf.getvalue()))

    stripped = strip_exif(image, original_format="PNG")
    assert stripped.info.get("Comment") is None


def test_blur_faces_disabled_returns_original():
    image = PILImage.new("RGB", (50, 50), color="red")
    result = blur_faces_and_tattoos(image, enabled=False)
    assert result is image


def test_blur_faces_without_opencv_returns_original_and_warns(caplog):
    image = PILImage.new("RGB", (50, 50), color="red")
    result = blur_faces_and_tattoos(image, enabled=True)
    assert result is image
    assert "opencv-python is not installed" in caplog.text


def test_is_opencv_available_returns_boolean():
    # This test simply verifies the helper returns a bool without crashing.
    assert isinstance(is_opencv_available(), bool)
