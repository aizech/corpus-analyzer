"""Automated legal/compliance invariant checks for Corpus Analyzer.

This script scans the codebase for patterns that could affect MDR, EU AI Act,
or GDPR Art. 9 classification. It is a tool for engineering and product; it
does not replace legal review.

Run from the repository root:
    python scripts/legal_compliance_check.py

Exit code 0 if all checks pass, non-zero otherwise.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Patterns that suggest triage/urgency classification.
TRAFFIC_LIGHT_PATTERNS = [
    r"\bred[-_ ]?flag\b",
    r"\btraffic[-_ ]?light\b",
    r"\bampel\b",
    r"\bdringend\b",
    r"\burgent\b",
    r"\bwithin\s+\d+\s+hours?\b",
    r"\bsofort\b",
    r"\bimmediately\b",
    r"\bnotfall\b",
    r"\bemergency\b",
    r"\b Screening \b",
    r"\bfrüherkennung\b",
    r"\bearly[-_ ]?detection\b",
    r"\btrack your cancer risk\b",
]

# Lines containing these negation words are usually disclaimers ("no urgent",
# "not an emergency", "avoid traffic-light").
TRIAGE_ALLOW_WORDS = {"not", "no", "never", "avoid", "without", "keine", "nicht"}

# Patterns that suggest a definitive diagnosis or treatment recommendation.
DIAGNOSIS_PATTERNS = [
    r"\bthis is\b.*\b(cancer|melanoma|infection|diagnosis)\b",
    r"\bthis is\b.*\b(harmless|benign|malignant)\b",
    r"\btake\b.*\b(antibiotics|medication|cream|ointment)\b",
    r"\bapply\b.*\b(cream|ointment|medication)\b",
    r"\bstart\s+treatment\b",
    r"\bstop\s+taking\b",
]

# Files that should contain only non-diagnostic, educational language.
USER_FACING_PATHS = [
    REPO_ROOT / "skills",
    REPO_ROOT / "views",
    REPO_ROOT / "translations.py",
    REPO_ROOT / "README.md",
    REPO_ROOT / "README_PRD.md",
]

# Python files that are part of the project (excludes venv and site-packages).
PROJECT_PYTHON_GLOB = [
    py
    for py in list(REPO_ROOT.glob("*.py"))
    + [
        p
        for d in REPO_ROOT.iterdir()
        if d.is_dir() and d.name not in {".venv", "venv", ".git"}
        for p in d.rglob("*.py")
    ]
    if py.is_file()
]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def check_progress_tracking_disabled_by_default() -> list[str]:
    """Verify that progress tracking defaults to False."""
    errors: list[str] = []
    config_text = _read_text(REPO_ROOT / "config.py")

    match = re.search(
        r"ENABLE_PROGRESS_TRACKING\s*=\s*os\.environ\.get\s*\(\s*['\"]ENABLE_PROGRESS_TRACKING['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)\.lower\(\)\s*in\s*\(([^)]+)\)",
        config_text,
        re.DOTALL,
    )
    if not match:
        errors.append("Could not parse ENABLE_PROGRESS_TRACKING default in config.py")
        return errors

    default_value = match.group(1).lower()
    truthy_values = {v.strip().strip("'\"") for v in match.group(2).split(",")}

    if default_value in truthy_values:
        errors.append(
            "ENABLE_PROGRESS_TRACKING default is truthy in config.py; must default to false"
        )
    return errors


def check_storage_requires_encryption_key() -> list[str]:
    """Verify that encrypted storage refuses to work without a key."""
    errors: list[str] = []
    storage_text = _read_text(REPO_ROOT / "storage" / "sqlite_storage.py")

    if 'raise ValueError("An encryption key is required' not in storage_text:
        errors.append("EncryptedSQLiteStorage does not explicitly require an encryption key")

    factory_text = _read_text(REPO_ROOT / "storage" / "factory.py")
    if "STORAGE_ENCRYPTION_KEY" not in factory_text:
        errors.append("Storage factory does not read STORAGE_ENCRYPTION_KEY")
    return errors


def _line_contains_negation(text: str, start: int, end: int) -> bool:
    """Check whether the surrounding line contains a negation/allow word."""
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end].lower()
    return any(word in line for word in TRIAGE_ALLOW_WORDS)


# Patterns that are acceptable inside README/PRD safety or policy sections.
TRIAGE_README_ALLOW = {r"\bemergency\b"}


def check_no_traffic_light_language() -> list[str]:
    """Scan user-facing files for traffic-light/triage language."""
    errors: list[str] = []
    for base_path in USER_FACING_PATHS:
        for path in base_path.rglob("*") if base_path.is_dir() else [base_path]:
            if not path.is_file() or path.suffix not in (".py", ".md", ".txt"):
                continue
            text = _read_text(path)
            for pattern in TRAFFIC_LIGHT_PATTERNS:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    if _line_contains_negation(text, match.start(), match.end()):
                        continue
                    if pattern in TRIAGE_README_ALLOW and path.name in {
                        "README.md",
                        "README_PRD.md",
                    }:
                        continue
                    line = text[: match.start()].count("\n") + 1
                    errors.append(
                        f"Possible triage language in {path.relative_to(REPO_ROOT)}:{line}: "
                        f"'{match.group(0)}'"
                    )
    return errors


def check_skills_avoid_diagnosis_claims() -> list[str]:
    """Verify that skills explicitly forbid diagnosis and treatment claims."""
    errors: list[str] = []
    disclaimers = [
        "not a diagnosis",
        "does not diagnose",
        "educational orientation",
        "not a treatment recommendation",
        "keine diagnose",
        "keine behandlungsempfehlung",
    ]
    skill_dir = REPO_ROOT / "skills"
    for skill_path in skill_dir.rglob("SKILL.md"):
        if skill_path.parent.name == "web-fetcher":
            # The web-fetcher is a tool, not a health-analysis skill.
            continue

        text_lower = _read_text(skill_path).lower()
        if not any(phrase in text_lower for phrase in disclaimers):
            errors.append(
                f"Skill {skill_path.relative_to(REPO_ROOT)} does not clearly disclaim diagnosis"
            )

        # Look for active diagnosis/treatment recommendations.
        for pattern in DIAGNOSIS_PATTERNS:
            for match in re.finditer(pattern, text_lower):
                if _line_contains_negation(text_lower, match.start(), match.end()):
                    continue
                line = text_lower[: match.start()].count("\n") + 1
                errors.append(
                    f"Possible diagnosis/treatment claim in {skill_path.relative_to(REPO_ROOT)}:{line}"
                )
    return errors


def check_progress_consent_is_separate() -> list[str]:
    """Verify the progress-tracking consent is a distinct UI element."""
    errors: list[str] = []
    view_text = _read_text(REPO_ROOT / "views" / "Medical_Image_Analysis.py")

    if "progress_tracking_consent" not in view_text:
        errors.append("Progress tracking consent not found in analysis view")
    if "progress_tracking_consent_checkbox" not in view_text:
        errors.append("Progress tracking consent checkbox key not found")
    return errors


def check_no_raw_image_logging() -> list[str]:
    """Verify that raw image bytes are not obviously logged by project code."""
    errors: list[str] = []
    for py_path in PROJECT_PYTHON_GLOB:
        if py_path.name == "legal_compliance_check.py":
            continue
        text = _read_text(py_path)
        # Look for logger calls that pass raw image variables (not just the word
        # "image" inside a human-readable warning string).
        for match in re.finditer(
            r"(logging|logger)\.(debug|info|warning|error|critical)\s*\([^)]*?\b(image_bytes|pil_image|encrypted_image|\.pil_image)\b",
            text,
            re.IGNORECASE,
        ):
            line = text[: match.start()].count("\n") + 1
            errors.append(f"Possible raw image logging in {py_path.relative_to(REPO_ROOT)}:{line}")
    return errors


def check_env_example_is_complete() -> list[str]:
    """Verify .env.example documents the environment variables used in config.py."""
    errors: list[str] = []
    config_text = _read_text(REPO_ROOT / "config.py")
    env_example_text = _read_text(REPO_ROOT / ".env.example")
    # Find os.environ.get("VAR_NAME", ...) or os.environ["VAR_NAME"] usages.
    env_vars = set(
        re.findall(r'os\.environ\.(?:get\(|\[)["\']([A-Z_][A-Z0-9_]*)["\']', config_text)
    )
    for var in env_vars:
        if var not in env_example_text:
            errors.append(f"Environment variable {var} is missing from .env.example")
    return errors


def check_no_hardcoded_secrets() -> list[str]:
    """Flag obvious hardcoded API keys or secrets in project Python files."""
    errors: list[str] = []
    secret_patterns = [
        r'["\']sk-[a-zA-Z0-9]{20,}["\']',
        r'["\']pk_[a-zA-Z0-9]{20,}["\']',
        r'["\']Bearer\s+[a-zA-Z0-9_-]{20,}["\']',
        r'["\']gh[pousr]_[a-zA-Z0-9_]{20,}["\']',
        r'["\']AKIA[0-9A-Z]{16}["\']',
    ]
    for py_path in PROJECT_PYTHON_GLOB:
        text = _read_text(py_path)
        for pattern in secret_patterns:
            for match in re.finditer(pattern, text):
                line = text[: match.start()].count("\n") + 1
                errors.append(
                    f"Possible hardcoded secret in {py_path.relative_to(REPO_ROOT)}:{line}"
                )
    return errors


def check_no_print_in_views() -> list[str]:
    """Views should use st.write / logger, not print, to avoid leaking data."""
    errors: list[str] = []
    for py_path in (REPO_ROOT / "views").rglob("*.py"):
        text = _read_text(py_path)
        for match in re.finditer(r"\bprint\s*\(", text):
            line = text[: match.start()].count("\n") + 1
            errors.append(
                f"Use logger or st.write instead of print in {py_path.relative_to(REPO_ROOT)}:{line}"
            )
    return errors


def check_progress_tracking_gate_in_ui() -> list[str]:
    """Verify progress tracking UI elements are gated by the feature flag."""
    errors: list[str] = []
    progress_view = _read_text(REPO_ROOT / "views" / "Progress.py")
    if "if not config.ENABLE_PROGRESS_TRACKING:" not in progress_view:
        errors.append("Progress.py does not guard against ENABLE_PROGRESS_TRACKING")

    analysis_view = _read_text(REPO_ROOT / "views" / "Medical_Image_Analysis.py")
    if "config.ENABLE_PROGRESS_TRACKING" not in analysis_view:
        errors.append("Medical_Image_Analysis.py does not reference ENABLE_PROGRESS_TRACKING")
    if (
        "_render_save_snapshot" in analysis_view
        and "progress_tracking_consent" not in analysis_view
    ):
        errors.append("Save-snapshot UI may not be gated by consent")
    return errors


def check_analysis_prompt_has_disclaimer() -> list[str]:
    """Verify the analysis prompt instructs the model to include a medical disclaimer."""
    errors: list[str] = []
    prompt_text = _read_text(REPO_ROOT / "analysis_prompt.py").lower()
    if "disclaimer" not in prompt_text:
        errors.append("analysis_prompt.py does not mention a medical disclaimer")
    diagnosis_disclaimers = [
        "not a diagnosis",
        "does not diagnose",
        "does not provide a medical diagnosis",
    ]
    if not any(phrase in prompt_text for phrase in diagnosis_disclaimers):
        errors.append("analysis_prompt.py does not clearly forbid diagnosis")
    return errors


def check_skills_have_safety_section() -> list[str]:
    """Verify health skills contain a safety rules section."""
    errors: list[str] = []
    skill_dir = REPO_ROOT / "skills"
    for skill_path in skill_dir.rglob("SKILL.md"):
        if skill_path.parent.name == "web-fetcher":
            continue
        text = _read_text(skill_path).lower()
        if "## safety" not in text and "safety rules" not in text:
            errors.append(f"Skill {skill_path.relative_to(REPO_ROOT)} is missing a safety section")
    return errors


CHECKS = [
    ("Progress tracking disabled by default", check_progress_tracking_disabled_by_default),
    ("Storage requires encryption key", check_storage_requires_encryption_key),
    ("No traffic-light/triage language", check_no_traffic_light_language),
    ("Skills disclaim diagnosis", check_skills_avoid_diagnosis_claims),
    ("Progress consent is separate", check_progress_consent_is_separate),
    ("No raw image logging", check_no_raw_image_logging),
    ("Environment variables documented", check_env_example_is_complete),
    ("No hardcoded secrets", check_no_hardcoded_secrets),
    ("No print statements in views", check_no_print_in_views),
    ("Progress tracking gated in UI", check_progress_tracking_gate_in_ui),
    ("Analysis prompt has disclaimer", check_analysis_prompt_has_disclaimer),
    ("Skills have safety section", check_skills_have_safety_section),
]


def main() -> int:
    """Run all checks and report results."""
    all_errors: list[str] = []
    print("Running legal/compliance invariant checks...\n")

    for name, check in CHECKS:
        errors = check()
        status = "PASS" if not errors else "FAIL"
        print(f"[{status}] {name}")
        for error in errors:
            print(f"  - {error}")
        all_errors.extend(errors)

    print()
    if all_errors:
        print(f"FAILED: {len(all_errors)} issue(s) found.")
        print("Review before enabling ENABLE_PROGRESS_TRACKING in production.")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
