"""Tests for the skill router."""

from pathlib import Path

from agent_config.skill_router import discover_catalog, select_candidates

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOTS = [REPO_ROOT / "skills" / "core"]


def test_discover_catalog_finds_medical_skill():
    catalog = discover_catalog(SKILL_ROOTS)
    names = {record.name for record in catalog}
    assert "medical-image-analysis" in names


def test_discover_catalog_finds_new_skills():
    catalog = discover_catalog(SKILL_ROOTS)
    names = {record.name for record in catalog}
    assert "skin-photo-analysis" in names
    assert "nail-photo-analysis" in names
    assert "document-explainer" in names
    assert "wound-photo-analysis" in names
    assert "rash-photo-analysis" in names
    assert "tick-bite-photo-analysis" in names
    assert "medication-package-analysis" in names
    assert "eye-throat-photo-analysis" in names


def test_select_candidates_prefers_medical_for_image_prompt():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("analyze this chest x-ray", catalog, limit=5)
    assert any(record.name == "medical-image-analysis" for record in candidates)


def test_select_candidates_prefers_skin_for_mole_prompt():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("mole on my arm changed color", catalog, limit=5)
    assert any(record.name == "skin-photo-analysis" for record in candidates)


def test_select_candidates_prefers_nail_for_nail_prompt():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("nail discoloration on big toe", catalog, limit=5)
    assert any(record.name == "nail-photo-analysis" for record in candidates)


def test_select_candidates_prefers_document_explainer_for_letter():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("explain this doctor's letter", catalog, limit=5)
    assert any(record.name == "document-explainer" for record in candidates)


def test_select_candidates_prefers_wound_for_cut_prompt():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("cut on my finger is not healing", catalog, limit=5)
    assert any(record.name == "wound-photo-analysis" for record in candidates)


def test_select_candidates_prefers_rash_for_itchy_red_prompt():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("itchy red rash on arm", catalog, limit=5)
    assert any(record.name == "rash-photo-analysis" for record in candidates)


def test_select_candidates_prefers_tick_bite_for_wandering_redness():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("tick bite with circular redness", catalog, limit=5)
    assert any(record.name == "tick-bite-photo-analysis" for record in candidates)


def test_select_candidates_prefers_medication_package_for_pill_box():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("explain this medication box", catalog, limit=5)
    assert any(record.name == "medication-package-analysis" for record in candidates)


def test_select_candidates_prefers_eye_throat_for_sore_throat():
    catalog = discover_catalog(SKILL_ROOTS)
    candidates = select_candidates("red sore throat photo", catalog, limit=5)
    assert any(record.name == "eye-throat-photo-analysis" for record in candidates)
