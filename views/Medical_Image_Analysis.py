import io

import numpy as np
import pydicom
import streamlit as st
from agno.media import Image as AgnoImage
from PIL import Image as PILImage

from agents.medical_agent import create_medical_imaging_agent
from analysis_format import confidence_level, parse_analysis_sections
from dicom_utils import anonymize_dicom_dataset, get_anonymization_report
from export import PDF_EXPORT_AVAILABLE, cached_markdown_report, cached_pdf_report
from models import get_default_model_id
from ui import (
    card,
    empty_state,
    inject_custom_css,
    render_page_header,
    render_sidebar_info,
    role_badge,
    workflow_steps,
)

ANALYZE_SPINNER = "Analyzing image... Please wait."
ROLES = ["clinician", "patient", "researcher"]


def _init_session() -> None:
    """Initialize session state keys used by this page."""
    defaults = {
        "user_role": "clinician",
        "additional_info": "",
        "analysis_results": {},
        "analysis_image_bytes": None,
        "analysis_model": "",
        "analysis_context": "",
    }
    # Migrate legacy single-analysis key to per-role storage.
    if "analysis_text" in st.session_state and "analysis_results" not in st.session_state:
        legacy_text = st.session_state.pop("analysis_text")
        defaults["analysis_results"] = {"clinician": legacy_text} if legacy_text else {}
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def _get_analysis_text(role: str) -> str:
    """Return the analysis text stored for the given role, if any."""
    return st.session_state.get("analysis_results", {}).get(role, "")


def _get_or_create_agent():
    """Return a cached medical imaging agent, creating it if necessary."""
    if "medical_agent" not in st.session_state or st.session_state.medical_agent is None:
        st.session_state.medical_agent = create_medical_imaging_agent(
            model_id=get_default_model_id()
        )
    return st.session_state.medical_agent


def _load_uploaded_image(uploaded_file, anonymize: bool = True):
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


def _resize_for_display(pil_image: PILImage.Image, max_width: int = 600) -> PILImage.Image:
    """Resize an image while preserving aspect ratio."""
    width, height = pil_image.size
    if width <= max_width:
        return pil_image
    aspect_ratio = width / height
    new_height = int(max_width / aspect_ratio)
    return pil_image.resize((max_width, new_height))


def _build_analysis_prompt(additional_info: str, role: str) -> str:
    """Build the prompt sent to the medical imaging agent."""
    role_instruction = {
        "clinician": (
            "You are writing for a qualified healthcare professional. "
            "Use precise radiology terminology, structured findings, and keep the tone concise and clinical."
        ),
        "patient": (
            "You are explaining the results to a patient with no medical background. "
            "Use plain language, avoid jargon, and focus on what the findings mean and what to do next."
        ),
        "researcher": (
            "You are writing for a medical researcher. Include technical detail, differential diagnoses, "
            "confidence discussion, and evidence-based references where possible."
        ),
    }.get(role, "")

    base = (
        "Analyze this medical image considering the following context: " + additional_info
        if additional_info
        else "Analyze this medical image and provide detailed findings."
    )

    return (
        f"Role: {role.capitalize()}\n\n"
        f"{role_instruction}\n\n"
        f"{base}\n\n"
        "If you are not sure about the diagnosis, please provide a possible diagnosis. "
        "Answer in the language of the user; if not specified, answer in English."
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


def _run_analysis(role: str, display_image: PILImage.Image) -> str:
    """Run the medical imaging agent for the given role and return the text response."""
    img_buf = io.BytesIO()
    display_image.save(img_buf, format="PNG")
    image_bytes = img_buf.getvalue()
    agno_image = AgnoImage(content=image_bytes, format="png")

    prompt = _build_analysis_prompt(
        st.session_state.additional_info,
        role,
    )
    agent = _get_or_create_agent()
    response = agent.run(prompt, images=[agno_image])
    analysis_text = _extract_response_text(response)

    st.session_state["analysis_image_bytes"] = image_bytes
    st.session_state["analysis_model"] = get_default_model_id()
    st.session_state["analysis_context"] = st.session_state.additional_info
    st.session_state["analysis_results"][role] = analysis_text
    return analysis_text


def _render_image_viewer(pil_image: PILImage.Image, display_image: PILImage.Image) -> None:
    """Render the uploaded image with a lightweight zoom viewer."""
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        st.markdown('<div class="ca-image-viewer">', unsafe_allow_html=True)
        st.image(display_image, caption="Uploaded Medical Image", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_consent() -> bool:
    """Render the privacy consent panel and return whether it is checked."""
    st.markdown(
        """
        <div class="ca-consent">
            <div class="ca-consent-title">Privacy confirmation required</div>
            <div style="margin-bottom: 0.5rem;">Before analysis, please confirm:</div>
            <ul class="ca-consent-list">
                <li>The image bytes will be sent to the selected AI provider.</li>
                <li>Your prompt text will be sent to the selected AI provider.</li>
                <li>DICOM metadata is anonymized locally and is not sent.</li>
                <li>Burned-in text/annotations inside the image pixels may still be visible.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Why is this required?"):
        st.write(
            "Medical images may contain protected health information (PHI). "
            "This confirmation helps ensure you do not accidentally send identifiable patient data "
            "to an external AI service."
        )
    return st.checkbox(
        "I confirm this upload and text contain no sensitive patient-identifying information",
        value=False,
        key="privacy_consent",
    )


def _render_prompt_templates() -> None:
    """Render quick prompt chips and the additional context text area."""
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

    st.caption("Quick prompts")
    cols = st.columns(len(prompt_templates))
    for (label, text), col in zip(prompt_templates.items(), cols, strict=False):
        with col:
            if st.button(label, use_container_width=True, key=f"tpl_{label}"):
                st.session_state.additional_info = text
                st.rerun()

    current = st.session_state.additional_info or ""
    st.text_area(
        "Provide additional context about the image (e.g., patient history, symptoms)",
        value=current,
        placeholder="Enter any relevant information here...  e.g. Antworte auf Deutsch",
        key="additional_info_input",
        height=180,
    )
    # Streamlit's key binding mutates the widget value; mirror it back to session state.
    st.session_state.additional_info = st.session_state.additional_info_input
    st.caption(f"{len(st.session_state.additional_info)} characters")


def _render_results(role: str) -> None:
    """Render parsed analysis results according to the selected role."""
    text = _get_analysis_text(role)
    if not text:
        return

    sections = parse_analysis_sections(text)
    confidence = confidence_level(text)

    st.markdown("## :material/medical_services: Analysis Results")
    col1, col2 = st.columns([1, 6])
    with col1:
        role_badge(role)
    with col2:
        if confidence:
            badge_class = f"ca-badge-confidence-{confidence}"
            st.markdown(
                f'<span class="ca-badge {badge_class}">Confidence: {confidence.capitalize()}</span>',
                unsafe_allow_html=True,
            )

    if role == "patient":
        _render_patient_view(sections, text)
    elif role == "researcher":
        _render_researcher_view(sections, text)
    else:
        _render_clinician_view(sections, text)

    _render_export_and_feedback(role)


def _render_clinician_view(sections: dict, raw_text: str) -> None:
    """Render a scannable clinician view of the report."""
    order = [
        "clinical interpretation",
        "professional analysis",
        "image technical assessment",
        "evidence-based context",
    ]
    for key in order:
        if key in sections:
            with st.expander(sections[key].split("\n")[0] if False else key.title(), expanded=True):
                st.markdown(sections[key])

    if "patient education" in sections:
        with st.expander("Patient Education", expanded=False):
            st.markdown(sections["patient education"])

    if "medical disclaimer" in sections:
        st.warning(sections["medical disclaimer"])
    elif "_raw" in sections:
        st.markdown(sections["_raw"])
        st.caption(
            "Note: This analysis is generated by AI and should be reviewed by "
            "a qualified healthcare professional."
        )


def _render_patient_view(sections: dict, raw_text: str) -> None:
    """Render a simplified patient-friendly view."""
    if "patient education" in sections:
        card("What this means", sections["patient education"], icon=":material/info:")
    elif "clinical interpretation" in sections:
        card("What this means", sections["clinical interpretation"], icon=":material/info:")

    if "clinical interpretation" in sections and "patient education" in sections:
        with st.expander("Clinical details", expanded=False):
            st.markdown(sections["clinical interpretation"])

    if "medical disclaimer" in sections:
        st.warning(sections["medical disclaimer"])
    elif "_raw" in sections:
        st.markdown(sections["_raw"])


def _render_researcher_view(sections: dict, raw_text: str) -> None:
    """Render the full structured report for researchers."""
    for key, body in sections.items():
        if key == "_raw":
            continue
        with st.expander(key.title(), expanded=True):
            st.markdown(body)
    with st.expander("Raw response", expanded=False):
        st.markdown(raw_text)


def _render_export_and_feedback(role: str) -> None:
    """Render download buttons and a quick rating widget."""
    image_bytes = st.session_state.get("analysis_image_bytes")
    analysis_text = _get_analysis_text(role)
    model_id = st.session_state.get("analysis_model", get_default_model_id())
    additional_context = st.session_state.get("analysis_context", "")

    if not image_bytes or not analysis_text:
        return

    st.markdown("---")
    st.markdown("### Report actions")
    md_content = cached_markdown_report(image_bytes, analysis_text, model_id, additional_context)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.download_button(
            label="Download Markdown",
            icon=":material/download:",
            data=md_content,
            file_name="corpus_analyzer_analysis.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        if PDF_EXPORT_AVAILABLE:
            pdf_content = cached_pdf_report(
                image_bytes, analysis_text, model_id, additional_context
            )
            st.download_button(
                label="Download PDF",
                icon=":material/download:",
                data=pdf_content,
                file_name="corpus_analyzer_analysis.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.caption("PDF export disabled")
    with col3:
        st.feedback("stars", key="analysis_rating")


def main() -> None:
    inject_custom_css()
    render_page_header(
        "Analyze",
        subtitle="Upload a medical image for professional analysis",
    )
    render_sidebar_info()
    _init_session()

    with st.sidebar:
        st.markdown("---")
        st.caption("User mode")
        selected_role = st.radio(
            "View results as",
            options=[r.capitalize() for r in ROLES],
            index=ROLES.index(st.session_state.user_role),
            key="role_selector",
        )
        st.session_state.user_role = selected_role.lower()

    upload_container = st.container()
    controls_container = st.container()
    analysis_container = st.container()

    with upload_container:
        uploaded_file = st.file_uploader(
            "Upload medical image",
            type=["jpg", "jpeg", "png", "dicom", "dcm"],
            help="Supported formats: JPG, JPEG, PNG, DICOM, DCM",
            label_visibility="collapsed",
        )

    if uploaded_file is None:
        empty_state(
            icon=":material/upload_file:",
            title="Upload a medical image to begin",
            description="Corpus Analyzer uses AI to provide educational analysis of X-rays, "
            "MRI, CT, and ultrasound images.",
        )
        workflow_steps()
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

    with controls_container:
        _render_image_viewer(pil_image, display_image)

        with st.expander("Image details", expanded=False):
            st.write(
                f"**Format:** {uploaded_file.type or uploaded_file.name.split('.')[-1].upper()}"
            )
            st.write(f"**Dimensions:** {pil_image.size[0]} x {pil_image.size[1]} pixels")
            if cleared_tags:
                st.write("**Cleared DICOM tags:**", ", ".join(cleared_tags))
            if removed_sequences:
                st.write("**Removed sequences:**", ", ".join(removed_sequences))
            if not cleared_tags and not removed_sequences:
                st.write("No DICOM metadata anonymization performed (standard image).")

        safe_to_send = _render_consent()

        _render_prompt_templates()

        analyze_button = st.button(
            "Analyze Image",
            icon=":material/search:",
            type="primary",
            use_container_width=True,
            disabled=not safe_to_send,
        )

    with analysis_container:
        if analyze_button:
            if not safe_to_send:
                st.error("Please confirm the privacy statement before analyzing.")
                return

            with st.spinner(ANALYZE_SPINNER):
                try:
                    _run_analysis(st.session_state.user_role, display_image)
                except Exception:
                    st.error(
                        "Sorry, we could not analyze the image. Please try again or contact support."
                    )
                    st.info(
                        "If the problem persists, check that your OpenAI API key is valid "
                        "and has access to the selected model."
                    )
                    import logging

                    logging.getLogger(__name__).exception("Image analysis failed")
                    return

        role = st.session_state.user_role
        if _get_analysis_text(role):
            _render_results(role)
        elif (
            _get_analysis_text("clinician")
            or _get_analysis_text("patient")
            or _get_analysis_text("researcher")
        ):
            st.info(
                f"Switching to **{role.capitalize()}** mode requires a new analysis tailored for that audience. "
                "Click the button below to re-analyze."
            )
            if st.button(
                f"Re-analyze as {role.capitalize()}",
                icon=":material/refresh:",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner(ANALYZE_SPINNER):
                    try:
                        _run_analysis(role, display_image)
                    except Exception:
                        st.error(
                            "Sorry, we could not analyze the image. Please try again or contact support."
                        )
                        st.info(
                            "If the problem persists, check that your OpenAI API key is valid "
                            "and has access to the selected model."
                        )
                        import logging

                        logging.getLogger(__name__).exception("Image analysis failed")
                        return
                st.rerun()


main()
