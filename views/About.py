"""About page for Corpus Analyzer."""

import streamlit as st

from config import config
from translations import format_text
from ui import render_page_header, section_header


def main():
    render_page_header(
        format_text("about_title"),
        subtitle=format_text("about_subtitle"),
    )

    section_header(format_text("about_what_does"))
    st.markdown(format_text("about_what_does_text"))

    section_header(format_text("about_how_to_use"))
    st.markdown(
        f"""
        1. {format_text("about_step1")}
        2. {format_text("about_step2")}
        3. {format_text("about_step3")}
        4. {format_text("about_step4")}
        5. {format_text("about_step5")}
        6. {format_text("about_step6")}
        7. {format_text("about_step7")}
        8. {format_text("about_step8")}
        """
    )

    section_header(format_text("about_research"))
    st.markdown(format_text("about_research_text"))

    section_header(format_text("about_important"))
    st.warning(format_text("about_important_warning"))

    section_header(format_text("about_resources"))
    st.markdown(
        f"- [{format_text('about_report_issue')}]({config.GITHUB_REPO_URL}/issues)\n"
        f"- [{format_text('about_request_feature')}]({config.GITHUB_REPO_URL}/issues)\n"
        f"- [{format_text('about_security_privacy')}](/Security)"
    )

    st.markdown("---")
    st.caption(
        '"Healthcare should be accessible, transparent, and empowering." — Bernhard Z., Founder of Corpus Analytica'
    )


main()
