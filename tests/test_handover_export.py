"""Tests for handover export functions."""

import io
from datetime import datetime, timezone

from PIL import Image as PILImage

from export import build_handover_markdown_report
from storage.models import PhotoSnapshot, SnapshotTag


def _make_image_bytes() -> bytes:
    buf = io.BytesIO()
    PILImage.new("RGB", (10, 10), color="blue").save(buf, format="PNG")
    return buf.getvalue()


def _make_snapshot(
    created_at: datetime,
    body_site: str = "front:chest",
    encrypted_image: bytes = b"",
) -> PhotoSnapshot:
    snapshot = PhotoSnapshot.create(
        user_id="user-1",
        image_hash="hash",
        body_site=body_site,
        anamnesis="Itches.",
        analysis_summary="Symmetrical spot.",
        encrypted_image=encrypted_image,
        tags=[SnapshotTag.SKIN],
        metadata={},
    )
    snapshot.created_at = created_at
    return snapshot


def test_handover_markdown_includes_timeline_and_disclaimer():
    image_bytes = _make_image_bytes()
    snapshots = [
        _make_snapshot(datetime(2026, 1, 1, tzinfo=timezone.utc), encrypted_image=image_bytes),
        _make_snapshot(datetime(2026, 2, 1, tzinfo=timezone.utc), encrypted_image=image_bytes),
    ]
    report = build_handover_markdown_report(snapshots, role="patient", user_id="user-1")

    assert "# Corpus Analyzer - Handover Report" in report
    assert "user-1" in report
    assert "Symmetrical spot" in report
    assert "Itches" in report
    assert "orientation" in report.lower()
    assert "not a diagnosis" in report.lower()
    assert "2026-02-01" in report
