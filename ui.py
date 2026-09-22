"""Shared Streamlit UI components for Corpus Analyzer pages."""

import re
from pathlib import Path
from typing import Optional

import streamlit as st

from config import config
from translations import _

_CSS_PATH = Path(__file__).parent / "assets" / "custom.css"
_MATERIAL_ICON_RE = re.compile(r":material/([a-z0-9_]+):")


def _render_icon_html(icon: str) -> str:
    """Convert a material icon reference or emoji/character into HTML.

    Supports ``:material/icon_name:`` syntax and falls back to plain text.
    """
    match = _MATERIAL_ICON_RE.fullmatch(icon.strip())
    if match:
        name = match.group(1)
        return f'<span class="material-symbols-rounded">{name}</span>'
    return f"<span>{icon}</span>"


def inject_custom_css() -> None:
    """Inject the custom stylesheet into the Streamlit app."""
    if _CSS_PATH.exists():
        st.markdown(
            f"<style>{_CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True
        )


def render_page_header(
    title: str,
    subtitle: Optional[str] = None,
    use_logo: bool = True,
) -> None:
    """Render the common page header with logo, title, and optional subtitle."""
    inject_custom_css()
    if use_logo:
        st.logo(config.LOGO_TEXT_PATH, size="large", icon_image=config.LOGO_ICON_PATH)

    header = st.container()
    with header:
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(config.LOGO_TEAM_PATH, width=100)
        with col2:
            st.markdown(
                f"""
                # {title}
                {f'<h3 style="font-size: 1.1rem; margin-top: 0.25rem; color: var(--ca-text-muted);">{subtitle}</h3>' if subtitle else ""}
                """,
                unsafe_allow_html=True,
            )


def render_sidebar_info() -> None:
    """Render the standard sidebar info and disclaimer."""
    with st.sidebar, st.expander(_("sidebar_safety_privacy"), expanded=False):
        st.info(_("sidebar_analysis_description"))
        st.warning(_("sidebar_disclaimer"))
        st.info(_("sidebar_dicom_note"))


def card(title: str, content: str, icon: Optional[str] = None) -> None:
    """Render a styled card with a title and markdown content."""
    icon_html = _render_icon_html(icon) if icon else ""
    st.markdown(
        f"""
        <div class="ca-card">
            <div class="ca-card-title">{icon_html} {title}</div>
            <div class="ca-card-muted">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: Optional[str] = None) -> None:
    """Render a section title with optional subtitle."""
    subtitle_html = f'<div class="ca-section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="ca-section-header">
            <div class="ca-section-title">{title}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(
    icon: str,
    title: str,
    description: str,
) -> None:
    """Render a centered empty-state panel."""
    icon_html = _render_icon_html(icon)
    st.markdown(
        f"""
        <div class="ca-empty">
            <div class="ca-empty-icon">{icon_html}</div>
            <div class="ca-empty-title">{title}</div>
            <div>{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def role_badge(role: str) -> None:
    """Render a badge for the selected user role."""
    role_class = {
        "clinician": "ca-badge-clinician",
        "patient": "ca-badge-patient",
        "researcher": "ca-badge-researcher",
    }.get(role.lower(), "ca-badge-clinician")
    role_label = {
        "clinician": _("role_clinician"),
        "patient": _("role_patient"),
        "researcher": _("role_researcher"),
    }.get(role.lower(), role.capitalize())
    st.markdown(
        f'<span class="ca-badge {role_class}">{role_label} {_("role_view")}</span>',
        unsafe_allow_html=True,
    )


def workflow_steps() -> None:
    """Render the 3-step analysis workflow."""
    st.markdown(
        f"""
        <div class="ca-workflow">
            <div class="ca-workflow-step">
                <span class="number">1</span> {_("workflow_step1")}
            </div>
            <div class="ca-workflow-step">
                <span class="number">2</span> {_("workflow_step2")}
            </div>
            <div class="ca-workflow-step">
                <span class="number">3</span> {_("workflow_step3")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
