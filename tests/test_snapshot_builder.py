"""Tests for snapshot builder."""

import hashlib

import pytest

from snapshot_builder import build_snapshot
from storage.models import SnapshotTag


def _make_images() -> list[dict[str, object]]:
    return [{"bytes": b"fake-image-bytes", "caption": "test", "source": "upload"}]


def test_build_snapshot_requires_images():
    with pytest.raises(ValueError, match="At least one image"):
        build_snapshot(
            user_id="user-1",
            images=[],
            body_site="front:chest",
            anamnesis={},
            analysis_text="text",
            role="patient",
            prompt="prompt",
        )


def test_build_snapshot_computes_image_hash():
    images = _make_images()
    snapshot = build_snapshot(
        user_id="user-1",
        images=images,
        body_site="front:chest",
        anamnesis={},
        analysis_text="Summary paragraph.\n\nDetails.",
        role="patient",
        prompt="Explain this skin mole",
    )
    expected_hash = hashlib.sha256(b"fake-image-bytes").hexdigest()
    assert snapshot.image_hash == expected_hash


def test_build_snapshot_detects_skin_tag():
    snapshot = build_snapshot(
        user_id="user-1",
        images=_make_images(),
        body_site="front:chest",
        anamnesis={},
        analysis_text="The mole appears symmetrical.",
        role="patient",
        prompt="skin mole",
    )
    assert SnapshotTag.SKIN in snapshot.tags


def test_build_snapshot_detects_document_tag():
    snapshot = build_snapshot(
        user_id="user-1",
        images=_make_images(),
        body_site=None,
        anamnesis={},
        analysis_text="This letter mentions elevated cholesterol.",
        role="patient",
        prompt="Explain this doctor's letter",
    )
    assert SnapshotTag.DOCUMENT in snapshot.tags


def test_build_snapshot_truncates_summary():
    analysis = "word " * 200
    snapshot = build_snapshot(
        user_id="user-1",
        images=_make_images(),
        body_site="front:chest",
        anamnesis={},
        analysis_text=analysis,
        role="patient",
        prompt="prompt",
    )
    assert len(snapshot.analysis_summary) <= 505
    assert snapshot.analysis_summary.endswith("...")


def test_build_snapshot_includes_anamnesis():
    snapshot = build_snapshot(
        user_id="user-1",
        images=_make_images(),
        body_site="front:chest",
        anamnesis={"itching": "yes", "pain": "no"},
        analysis_text="Analysis.",
        role="patient",
        prompt="prompt",
    )
    assert snapshot.anamnesis is not None
    assert "itching: yes" in snapshot.anamnesis
    assert "pain: no" in snapshot.anamnesis
