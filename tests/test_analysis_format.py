"""Tests for analysis output parsing and formatting."""

from analysis_format import confidence_level, parse_analysis_sections

SAMPLE_ANALYSIS = """
### 1. Image Technical Assessment
Chest X-ray, PA view.

### 2. Professional Analysis
No acute findings.

### 3. Clinical Interpretation
Normal chest X-ray with high confidence.

### 4. Patient Education
Your chest X-ray looks normal.

### 5. Evidence-Based Context
References here.

### 6. Medical Disclaimer
This analysis is for educational purposes only.
"""


def test_parse_analysis_sections_finds_all_sections():
    sections = parse_analysis_sections(SAMPLE_ANALYSIS)
    assert "image technical assessment" in sections
    assert "professional analysis" in sections
    assert "clinical interpretation" in sections
    assert "patient education" in sections
    assert "evidence-based context" in sections
    assert "medical disclaimer" in sections


def test_parse_analysis_sections_returns_raw_when_no_sections():
    text = "No sections here."
    sections = parse_analysis_sections(text)
    assert "_raw" in sections
    assert sections["_raw"] == text


def test_confidence_level_detects_high():
    assert confidence_level("Findings suggest pneumonia with high confidence.") == "high"


def test_confidence_level_detects_uncertain():
    assert confidence_level("The diagnosis is uncertain.") == "uncertain"


def test_confidence_level_returns_none_when_missing():
    assert confidence_level("The image shows normal anatomy.") is None
