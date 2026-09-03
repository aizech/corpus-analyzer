"""Tests for the skill router."""

from pathlib import Path

from agent_config.skill_router import discover_catalog, select_candidates

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOTS = [REPO_ROOT / "skills" / "core"]


def test_discover_catalog_finds_medical_skill():
    catalog = discover_catalog(SKILL_ROOTS)
    names = {record.name for record in catalog}
    assert "medical-image-analysis" in names


def test_select_candidates_prefers_medical_for_image_prompt():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("analyze this chest x-ray", catalog, limit=5)
    assert any(record.name == "medical-image-analysis" for record in candidates)
