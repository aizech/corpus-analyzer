"""Shared Streamlit UI components for Corpus Analyzer pages."""

from typing import Optional

import streamlit as st

from config import config

APP_ICON = "material/diagnosis"


def render_page_header(
    title: str,
    subtitle: Optional[str] = None,
    page_icon: Optional[str] = None,
    use_logo: bool = True,
) -> None:
    """Render the common page header with logo, title, and optional subtitle."""
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
                # {config.APP_NAME}
                {f"## {subtitle}" if subtitle else ""}
                """,
                unsafe_allow_html=True,
            )


def render_sidebar_info() -> None:
    """Render the standard sidebar info and disclaimer."""
    with st.sidebar:
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
