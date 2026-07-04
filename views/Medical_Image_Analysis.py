import io

import numpy as np
import pydicom
import streamlit as st
from agno.media import Image as AgnoImage
from PIL import Image as PILImage

from agents.medical_agent import create_medical_imaging_agent
from dicom_utils import anonymize_dicom_dataset, get_anonymization_report
from export import PDF_EXPORT_AVAILABLE, cached_markdown_report, cached_pdf_report
from models import get_default_model_id
from ui import render_page_header, render_sidebar_info

ANALYZE_SPINNER = "Analyzing image... Please wait."


def _get_or_create_agent():
    """Return a cached medical imaging agent, creating it if necessary."""
    if "medical_agent" not in st.session_state or st.session_state.medical_agent is None:
        st.session_state.medical_agent = create_medical_imaging_agent(
            model_id=get_default_model_id()
        )
    return st.session_state.medical_agent


def _load_uploaded_image(uploaded_file, anonymize: bool = True) -> PILImage.Image:
    """Convert an uploaded file to a PIL Image, handling DICOM anonymization."""
    file_extension = uploaded_file.name.split(".")[-1].lower()
    is_dicom = file_extension in ["dicom", "dcm"] or uploaded_file.type == "application/dicom"

    if is_dicom:
        uploaded_file.seek(0)
        dicom_data = pydicom.dcmread(uploaded_file)
        cleared, removed = get_anonymization_report(dicom_data)
        dicom_for_use = anonymize_dicom_dataset(dicom_data) if anonymize else dicom_data

        img_array = dicom_for_use.pixel_array
        img_array = img_array / img_array.max() * 255
        img_array = img_array.astype(np.uint8)

        pil_image = PILImage.fromarray(img_array)
        if len(img_array.shape) == 2:
            pil_image = pil_image.convert("RGB")

        return pil_image, cleared, removed

    pil_image = PILImage.open(uploaded_file)
    return pil_image, [], []


def _resize_for_display(pil_image: PILImage.Image, max_width: int = 500) -> PILImage.Image:
    """Resize an image while preserving aspect ratio."""
    width, height = pil_image.size
    aspect_ratio = width / height
    new_height = int(max_width / aspect_ratio)
    return pil_image.resize((max_width, new_height))


def _build_analysis_prompt(additional_info: str) -> str:
    """Build the prompt sent to the medical imaging agent."""
    base = (
        "Analyze this medical image considering the following context: " + additional_info
        if additional_info
        else "Analyze this medical image and provide detailed findings."
    )
    return (
        base
        + "\n\nIf you are not sure about the diagnosis, please provide a possible diagnosis."
        + "\n\nAnswer in the language of the user. If it is not given, answer English."
    )


def _extract_response_text(response) -> str:
    """Extract the text content from an Agno response."""
    if hasattr(response, "content"):
        return str(response.content)
    if isinstance(response, str):
        return response
    if isinstance(response, dict) and "content" in response:
        return str(response["content"])
    return str(response)


def main():
    render_page_header(
        "Medical Image Analysis",
        subtitle="Upload a medical image for professional analysis",
        page_icon="material/diagnosis",
    )
    render_sidebar_info()

    upload_container = st.container()
    image_container = st.container()
    analysis_container = st.container()

    with upload_container:
        uploaded_file = st.file_uploader(
            "Upload medical image",
            type=["jpg", "jpeg", "png", "dicom", "dcm"],
            help="Supported formats: JPG, JPEG, PNG, DICOM, DCM",
            label_visibility="collapsed",
        )

    if uploaded_file is None:
        st.info(":material/upload: Please upload a medical image to begin analysis")
        return

    try:
        pil_image, cleared_tags, removed_sequences = _load_uploaded_image(
            uploaded_file, anonymize=True
        )
        display_image = _resize_for_display(pil_image)
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        st.info("Please upload a valid JPG, PNG, or DICOM file and try again.")
        return

    with image_container:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(display_image, caption="Uploaded Medical Image", use_container_width=True)

    with image_container:
        st.warning(
            "Anything visible in the image pixels and anything you type below may be sent to the AI provider. "
            "Do not include patient-identifying information."
        )

        with st.expander("Anonymization details", expanded=False):
            if cleared_tags:
                st.write("Cleared DICOM tags:", ", ".join(cleared_tags))
            else:
                st.write("No standard identifying DICOM tags found.")
            if removed_sequences:
                st.write("Removed sequences:", ", ".join(removed_sequences))
            st.caption(
                "Burned-in annotations or text embedded in the image pixels are not removed."
            )

        safe_to_send = st.checkbox(
            "I confirm this upload and text contain no sensitive patient-identifying information",
            value=False,
        )

        analyze_button = st.button(
            ":material/search: Analyze Image",
            type="primary",
            use_container_width=True,
            disabled=not safe_to_send,
        )

        if "additional_info" not in st.session_state:
            st.session_state.additional_info = ""

        prompt_templates = {
            "Answer in English": "Answer in English.",
            "Antworte auf Deutsch": "Antworte auf Deutsch.",
            "Radiology-style report": (
                "Provide a radiology-style report with:\n"
                "- Modality and study type (if apparent)\n"
                "- Key findings\n"
                "- Impression (most likely diagnosis + differential)\n"
                "- Recommended next steps\n"
                "Keep it concise."
            ),
            "Explain for patient": "Explain the findings in simple, patient-friendly language.",
            "Focus: red flags": "Focus on urgent findings / red flags and what to do next.",
            "Add patient context": (
                "Patient context:\n"
                "- Age: \n"
                "- Sex: \n"
                "- Symptoms: \n"
                "- Relevant history: \n"
                "- Clinical question: \n"
            ),
        }

        colp0, colp1, colp2, colp3, colp4 = st.columns([1.2, 6, 1, 1, 1])
        with colp0:
            st.caption("Quick prompts")
        with colp1:
            selected_template = st.selectbox(
                "Quick prompts",
                options=list(prompt_templates.keys()),
                index=0,
                key="quick_prompt_selector",
                label_visibility="collapsed",
            )
        with colp2:
            if st.button(
                ":material/input:",
                use_container_width=True,
                help="Replace the text field with this template",
            ):
                st.session_state.additional_info = prompt_templates[selected_template]
                st.rerun()
        with colp3:
            if st.button(
                ":material/playlist_add:",
                use_container_width=True,
                help="Append this template to the text field",
            ):
                existing = (st.session_state.additional_info or "").strip()
                addition = prompt_templates[selected_template].strip()
                st.session_state.additional_info = (
                    f"{existing}\n\n{addition}" if existing else addition
                )
                st.rerun()
        with colp4:
            if st.button(
                ":material/delete:",
                use_container_width=True,
                help="Clear the text field",
            ):
                st.session_state.additional_info = ""
                st.rerun()

        additional_info = st.text_area(
            "Provide additional context about the image (e.g., patient history, symptoms)",
            placeholder="Enter any relevant information here...  e.g. Antworte auf Deutsch",
            key="additional_info",
            height=250,
        )

    with analysis_container:
        if analyze_button:
            with st.spinner(ANALYZE_SPINNER):
                try:
                    img_buf = io.BytesIO()
                    display_image.save(img_buf, format="PNG")
                    image_bytes = img_buf.getvalue()
                    agno_image = AgnoImage(content=image_bytes, format="png")

                    prompt = _build_analysis_prompt(additional_info)
                    agent = _get_or_create_agent()
                    response = agent.run(prompt, images=[agno_image])
                    analysis_text = _extract_response_text(response)

                    st.session_state["analysis_image_bytes"] = image_bytes
                    st.session_state["analysis_text"] = analysis_text
                    st.session_state["analysis_model"] = get_default_model_id()
                    st.session_state["analysis_context"] = additional_info

                except Exception:
                    st.error(
                        "Sorry, we could not analyze the image. Please try again or contact support."
                    )
                    st.info(
                        "If the problem persists, check that your OpenAI API key is valid and has access to the selected model."
                    )
                    # Log the full error server-side; do not expose it to the UI.
                    import logging

                    logging.getLogger(__name__).exception("Image analysis failed")
                    return

        if "analysis_text" in st.session_state and st.session_state["analysis_text"]:
            st.markdown("### :material/diagnosis: Analysis Results")
            st.markdown("---")
            st.markdown(st.session_state["analysis_text"])
            st.markdown("---")
            st.caption(
                "Note: This analysis is generated by AI and should be reviewed by "
                "a qualified healthcare professional."
            )

            _render_export_buttons()


def _render_export_buttons() -> None:
    """Render download buttons for Markdown and PDF exports."""
    image_bytes = st.session_state.get("analysis_image_bytes")
    analysis_text = st.session_state.get("analysis_text", "")
    model_id = st.session_state.get("analysis_model", get_default_model_id())
    additional_context = st.session_state.get("analysis_context", "")

    if not image_bytes or not analysis_text:
        return

    md_content = cached_markdown_report(image_bytes, analysis_text, model_id, additional_context)

    if PDF_EXPORT_AVAILABLE:
        pdf_content = cached_pdf_report(image_bytes, analysis_text, model_id, additional_context)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label=":material/download: Download Markdown",
                data=md_content,
                file_name="corpus_analyzer_analysis.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                label=":material/download: Download PDF",
                data=pdf_content,
                file_name="corpus_analyzer_analysis.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    else:
        st.download_button(
            label=":material/download: Download Markdown",
            data=md_content,
            file_name="corpus_analyzer_analysis.md",
            mime="text/markdown",
            use_container_width=True,
        )


main()
