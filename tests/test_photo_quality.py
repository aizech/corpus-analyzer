"""Tests for photo quality helpers."""

from PIL import Image as PILImage

from photo_quality import assess_image_quality, quality_warning_text


def _make_image(mode: str = "RGB", color: int | tuple = (128, 128, 128)) -> PILImage.Image:
    return PILImage.new(mode, (100, 100), color=color)


def test_assess_image_quality_returns_expected_keys():
    image = _make_image()
    result = assess_image_quality(image)
    assert set(result.keys()) == {"blur_score", "brightness", "contrast", "warnings"}
    assert isinstance(result["blur_score"], float)
    assert 0 <= result["brightness"] <= 255
    assert result["contrast"] >= 0


def test_dark_image_warns():
    image = PILImage.new("RGB", (100, 100), color=(10, 10, 10))
    result = assess_image_quality(image)
    assert "too_dark" in result["warnings"]


def test_bright_image_warns():
    image = PILImage.new("RGB", (100, 100), color=(240, 240, 240))
    result = assess_image_quality(image)
    assert "too_bright" in result["warnings"]


def test_blurry_image_warns():
    # A perfectly uniform image has zero Laplacian variance.
    image = PILImage.new("RGB", (100, 100), color=(128, 128, 128))
    result = assess_image_quality(image)
    assert "too_blurry" in result["warnings"]


def test_quality_warning_text_returns_translated_messages():
    warnings = ["too_dark", "too_blurry"]
    text_en = quality_warning_text(warnings, language="en")
    assert "dark" in text_en.lower()
    assert "blurry" in text_en.lower()

    text_de = quality_warning_text(warnings, language="de")
    assert "dunkel" in text_de.lower()
    assert "unscharf" in text_de.lower()


def test_quality_warning_text_empty_for_no_warnings():
    assert quality_warning_text([]) == ""
