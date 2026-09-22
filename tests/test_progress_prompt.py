"""Tests for the progress comparison prompt builder."""

from datetime import datetime, timezone

from progress_prompt import build_comparison_prompt
from storage.models import PhotoSnapshot


def _make_snapshot(created_at: datetime, body_site: str = "front:chest") -> PhotoSnapshot:
    return PhotoSnapshot.create(
        user_id="user-1",
        image_hash="hash",
        body_site=body_site,
        anamnesis="Itches.",
        analysis_summary="Symmetrical spot.",
        tags=[],
    )


def test_prompt_includes_abcde():
    earlier = _make_snapshot(datetime(2026, 1, 1, tzinfo=timezone.utc))
    later = _make_snapshot(datetime(2026, 2, 1, tzinfo=timezone.utc))
    prompt = build_comparison_prompt(earlier, later)

    assert "ABCDE" in prompt
    assert "asymmetry" in prompt.lower()
    assert "border" in prompt.lower()
    assert "color" in prompt.lower()
    assert "diameter" in prompt.lower() or "size" in prompt.lower()
    assert "evolution" in prompt.lower() or "time" in prompt.lower()


def test_prompt_forbids_diagnosis_and_urgency():
    earlier = _make_snapshot(datetime(2026, 1, 1, tzinfo=timezone.utc))
    later = _make_snapshot(datetime(2026, 2, 1, tzinfo=timezone.utc))
    prompt = build_comparison_prompt(earlier, later)

    # We do not assert exact wording, but the prompt should explicitly avoid
    # diagnostic and triage language.
    assert "Do not diagnose" in prompt
    assert "Do not classify urgency" in prompt


def test_prompt_respects_language():
    earlier = _make_snapshot(datetime(2026, 1, 1, tzinfo=timezone.utc))
    later = _make_snapshot(datetime(2026, 2, 1, tzinfo=timezone.utc))
    prompt = build_comparison_prompt(earlier, later, language="de")
    assert "Answer in German" in prompt


def test_prompt_includes_snapshot_details():
    earlier = _make_snapshot(datetime(2026, 1, 1, tzinfo=timezone.utc), body_site="front:chest")
    later = _make_snapshot(datetime(2026, 2, 1, tzinfo=timezone.utc), body_site="front:chest")
    prompt = build_comparison_prompt(earlier, later, role="patient")
    assert earlier.created_at.isoformat() in prompt
    assert later.created_at.isoformat() in prompt
    assert "Body site" in prompt
    assert "plain language" in prompt.lower()
