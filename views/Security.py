import streamlit as st

from ui import card, render_page_header, section_header


def main():
    render_page_header(
        "Security",
        subtitle="Security & Privacy",
    )

    section_header("How your data is handled")

    card(
        title="Upload",
        content=(
            "Uploaded images (JPG/PNG), DICOM files, and photographed documents are received via "
            "Streamlit's file uploader and kept in memory for the current session only. "
            "By default, nothing is written to disk or stored between sessions."
        ),
        icon=":material/upload:",
    )
    card(
        title="DICOM anonymization",
        content=(
            "If you upload a DICOM file (``.dcm``/``.dicom``), common identifying metadata tags are "
            "cleared locally before analysis. Burned-in annotations or text embedded in the image "
            "pixels are not removed."
        ),
        icon=":material/shield:",
    )
    card(
        title="Photo privacy",
        content=(
            "Smartphone photos can contain EXIF metadata including GPS coordinates. Before analysis, "
            "EXIF/GPS data is stripped locally. Optional face/tattoo masking is available as an "
            "experimental, disabled-by-default feature."
        ),
        icon=":material/photo_camera:",
    )
    card(
        title="What is sent",
        content=(
            "Only your prompt text and the image/document bytes are sent to the configured AI "
            "provider (e.g., OpenAI) to generate an analysis."
        ),
        icon=":material/send:",
    )
    card(
        title="What is not stored",
        content=(
            "The app does not write uploaded images to disk as part of analysis. Sessions are "
            "temporary. Progress tracking over time is planned as a strictly opt-in, encrypted, "
            "deletable feature and is not active in this release."
        ),
        icon=":material/delete_forever:",
    )

    section_header("Data protection law")
    st.markdown(
        "Health data is special-category data under **GDPR Art. 9**. Corpus Analyzer is designed "
        "for de-identified, educational use. HIPAA considerations apply for US contexts. "
        "Before any progress-tracking or triage-related features are released, the legal basis, "
        "processor agreements, and any cross-border data transfers must be clarified."
    )

    section_header("Data retention at the AI provider")
    st.markdown(
        "We use OpenAI models via the OpenAI API. OpenAI states that API inputs/outputs are "
        "**not used to train** OpenAI models **by default**, and we do not explicitly opt in. "
        "OpenAI retains certain request/response data for abuse monitoring and safety purposes for 30 days, "
        "after which it is deleted. Always verify the current policy at the link below."
    )
    st.link_button(
        "OpenAI: How your data is used",
        "https://platform.openai.com/docs/guides/your-data",
    )

    section_header("Contact")
    st.markdown(
        "Questions or vulnerability reports? Contact us at **support@corpusanalytica.com**."
    )


main()
