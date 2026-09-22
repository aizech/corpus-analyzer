"""About page for Corpus Analyzer."""

import streamlit as st

from config import config
from ui import render_page_header, section_header


def main():
    render_page_header(
        "About",
        subtitle="Corpus Analyzer",
    )

    section_header("What Corpus Analyzer does")
    st.markdown(
        "Corpus Analyzer is an educational tool that helps you understand what your images and "
        "documents show. Upload an X-ray, MRI, CT, ultrasound, or DICOM image; a smartphone photo "
        "of a mole, nail, rash, or wound; or a photographed doctor's letter, lab report, or "
        "medication package. You will receive a structured, AI-generated report tailored to your "
        "role — patient, clinician, or researcher."
    )

    section_header("How to use it")
    st.markdown(
        """
        1. Go to **Analyze** and upload or capture one or more images or documents.
        2. Confirm that the images contain no patient-identifying information.
        3. Choose the response **language** (English or Deutsch) in the sidebar.
        4. Select one or more **quick prompts** (e.g., radiology style, red flags, online research)
           or type your own context.
        5. Optionally fill in the **anamnesis** questions to give the model more context.
        6. Click **Analyze** and wait for the structured report.
        7. Switch between **Clinician**, **Patient**, and **Researcher** views. Each mode generates
           a report tailored for that audience; switching modes after an analysis offers a
           **Re-analyze** button for the new role.
        8. Download the report as Markdown or PDF.
        """
    )

    section_header("Research & references")
    st.markdown(
        "The **Online research** quick prompt asks the model to include current authoritative "
        "references (for example PubMed, medical society guidelines, or clinical journal articles) "
        "and cite them with URLs. Corpus Analyzer uses a local web-fetcher tool for live page retrieval."
    )

    section_header("Important")
    st.warning(
        "This tool is for educational and orientation purposes only. It is not CE-marked or "
        "FDA-cleared for clinical decision-making. All analyses should be reviewed by qualified "
        "healthcare professionals. Always consult a qualified healthcare provider for medical "
        "advice, diagnosis, or treatment."
    )

    section_header("Resources")
    st.markdown(
        f"- [Report an issue]({config.GITHUB_REPO_URL}/issues)\n"
        f"- [Request a feature]({config.GITHUB_REPO_URL}/issues)\n"
        f"- [Security & Privacy](/Security)"
    )

    st.markdown("---")
    st.caption(
        '"Healthcare should be accessible, transparent, and empowering." — Bernhard Z., Founder of Corpus Analytica'
    )


main()
