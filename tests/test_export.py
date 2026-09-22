"""Tests for report export helpers."""

import pytest
from PIL import Image

from export import PDF_EXPORT_AVAILABLE, build_markdown_report, build_pdf_report


def _make_image(color: str = "red"):
    return Image.new("RGB", (100, 100), color=color)


def test_build_markdown_report_contains_image_and_analysis():
    img = _make_image()
    text = "Test analysis text"
    md = build_markdown_report(img, text, "openai:gpt-5.4-mini", "context")
    assert text in md
    assert "data:image/png;base64" in md
    assert "Corpus Analyzer" in md
    assert "Image Analysis Report" in md


def test_build_markdown_report_with_additional_images():
    img1 = _make_image("red")
    img2 = _make_image("blue")
    md = build_markdown_report(
        img1,
        "Analysis",
        "openai:gpt-5.4-mini",
        additional_images=[img2],
    )
    assert "## Uploaded Image(s)" in md
    assert "### Image 2" in md
    assert md.count("data:image/png;base64") == 2


def test_build_pdf_report_returns_bytes():
    if not PDF_EXPORT_AVAILABLE:
        pytest.skip("PDF export is disabled or fpdf2 is not installed")
    img = _make_image()
    text = "Test analysis text"
    pdf_bytes = build_pdf_report(img, text, "openai:gpt-5.4-mini")
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")


def test_build_pdf_report_with_additional_images():
    if not PDF_EXPORT_AVAILABLE:
        pytest.skip("PDF export is disabled or fpdf2 is not installed")
    img1 = _make_image("red")
    img2 = _make_image("blue")
    pdf_bytes = build_pdf_report(img1, "Analysis", "openai:gpt-5.4-mini", additional_images=[img2])
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
