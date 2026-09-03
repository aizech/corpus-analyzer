"""Shared Streamlit UI components for Corpus Analyzer pages."""

from pathlib import Path
from typing import Optional

import streamlit as st

from config import config

_CSS_PATH = Path(__file__).parent / "assets" / "custom.css"


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
    with st.sidebar, st.expander("Safety & Privacy", expanded=False):
        st.info(
            "This tool provides AI-powered analysis of medical imaging data using "
            "advanced computer vision and radiological expertise."
        )
        st.warning(
            "DISCLAIMER: This tool is for educational and informational purposes only. "
            "All analyses should be reviewed by qualified healthcare professionals. "
            "Do not make medical decisions based solely on this analysis."
        )
        st.info(
            "DICOM files are anonymized locally (common identifying tags cleared) before analysis. "
            "This does not remove burned-in annotations in pixel data."
        )


def card(title: str, content: str, icon: Optional[str] = None) -> None:
    """Render a styled card with a title and markdown content."""
    icon_html = f"<span>{icon}</span>" if icon else ""
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
    st.markdown(
        f"""
        <div class="ca-empty">
            <div class="ca-empty-icon">{icon}</div>
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
    st.markdown(
        f'<span class="ca-badge {role_class}">{role.capitalize()} view</span>',
        unsafe_allow_html=True,
    )


def workflow_steps() -> None:
    """Render the 3-step analysis workflow."""
    st.markdown(
        """
        <div class="ca-workflow">
            <div class="ca-workflow-step">
                <span class="number">1</span> Upload image
            </div>
            <div class="ca-workflow-step">
                <span class="number">2</span> Confirm privacy
            </div>
            <div class="ca-workflow-step">
                <span class="number">3</span> Get analysis
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
