import io
from typing import Dict, List, Optional

import streamlit as st
from agno.media import Image as AgnoImage
from PIL import Image as PILImage

from agents.medical_agent import create_medical_imaging_agent
from analysis_format import confidence_level, parse_analysis_sections
from export import PDF_EXPORT_AVAILABLE, cached_markdown_report, cached_pdf_report
from image_loader import LoadedImage, load_camera_shot, load_images, resize_for_display
from models import get_default_model_id
from photo_privacy import blur_faces_and_tattoos, strip_exif
from ui import (
    card,
    empty_state,
    inject_custom_css,
    render_page_header,
    render_sidebar_info,
    role_badge,
    workflow_steps,
)

ANALYZE_SPINNER = "Analyzing... Please wait."
ROLES = ["clinician", "patient", "researcher"]


def _init_session() -> None:
    """Initialize session state keys used by this page."""
    defaults: Dict[str, object] = {
        "user_role": "clinician",
        "user_language": "en",
        "additional_info": "",
        "analysis_results": {},
        "analysis_images": [],  # list of {"bytes": bytes, "caption": str, "source": str}
        "analysis_model": "",
        "analysis_context": "",
        "photo_anamnesis": {},
        "privacy_strip_exif": True,
        "privacy_blur_faces": False,
        "selected_prompts": [],
        "custom_context": "",
    }
    # Migrate legacy single-analysis key to per-role storage.
    if "analysis_text" in st.session_state and "analysis_results" not in st.session_state:
        legacy_text = st.session_state.pop("analysis_text")
        defaults["analysis_results"] = {"clinician": legacy_text} if legacy_text else {}

    # Migrate legacy single image bytes to gallery list.
    if "analysis_image_bytes" in st.session_state and "analysis_images" not in st.session_state:
        legacy_bytes = st.session_state.pop("analysis_image_bytes")
        if legacy_bytes:
            defaults["analysis_images"] = [
                {"bytes": legacy_bytes, "caption": "Uploaded image", "source": "upload"}
            ]

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


def _pil_to_bytes(pil_image: PILImage.Image) -> bytes:
    """Serialize a PIL image to PNG bytes."""
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    return buf.getvalue()


def _apply_privacy(image: PILImage.Image, original_format: Optional[str] = None) -> PILImage.Image:
    """Apply selected privacy transforms to a single image."""
    if st.session_state.privacy_strip_exif:
        image = strip_exif(image, original_format=original_format)
    if st.session_state.privacy_blur_faces:
        image = blur_faces_and_tattoos(image, enabled=True)
    return image


def _add_to_gallery(items: List[Dict[str, object]]) -> None:
    """Append new images to the session gallery, avoiding exact byte duplicates."""
    existing = {item["bytes"] for item in st.session_state.analysis_images}
    for item in items:
        if item["bytes"] not in existing:
            st.session_state.analysis_images.append(item)
            existing.add(item["bytes"])


def _gallery_to_loaded_images() -> List[LoadedImage]:
    """Convert the current session gallery into LoadedImage instances."""
    loaded: List[LoadedImage] = []
    for item in st.session_state.analysis_images:
        pil_image = PILImage.open(io.BytesIO(item["bytes"]))
        loaded.append(
            LoadedImage(
                pil_image=pil_image,
                source_type=item.get("source", "session"),
                original_name=item.get("caption"),
                is_dicom=False,
                cleared_tags=[],
                removed_sequences=[],
            )
        )
    return loaded


def _build_anamnesis_text() -> str:
    """Build a short anamnesis paragraph from session state."""
    anamnesis = st.session_state.get("photo_anamnesis", {})
    if not anamnesis:
        return ""

    parts: List[str] = []
    mapping = {
        "since_when": "Since when",
        "has_changed": "Has it changed",
        "itching": "Itching",
        "bleeding": "Bleeding",
        "pain": "Pain",
        "size_approx": "Approximate size",
        "additional_notes": "Additional notes",
    }
    for key, label in mapping.items():
        value = anamnesis.get(key)
        if value:
            parts.append(f"- {label}: {value}")

    if not parts:
        return ""
    return "Anamnesis:\n" + "\n".join(parts)


def _build_analysis_prompt(additional_info: str, role: str, language: str) -> str:
    """Build the prompt sent to the medical imaging agent."""
    role_instruction = {
        "clinician": (
            "You are writing for a qualified healthcare professional. "
            "Use precise terminology, structured findings, and keep the tone concise and clinical."
        ),
        "patient": (
            "You are explaining the results to a patient with no medical background. "
            "Use plain language, avoid jargon, and focus on what the findings mean and what to do next."
        ),
        "researcher": (
            "You are writing for a medical researcher. Include technical detail, differential considerations, "
            "confidence discussion, and evidence-based references where possible."
        ),
    }.get(role, "")

    language_instruction = {
        "de": "Answer in German.",
        "en": "Answer in English.",
    }.get(language, "Answer in the language of the user; if not specified, answer in English.")

    anamnesis_text = _build_anamnesis_text()

    base_parts: List[str] = []
    if additional_info:
        base_parts.append(
            "Analyze the provided image(s) considering the following context: " + additional_info
        )
    else:
        base_parts.append("Analyze the provided image(s) and provide detailed findings.")

    if anamnesis_text:
        base_parts.append(anamnesis_text)

    base = "\n\n".join(base_parts)

    return (
        f"Role: {role.capitalize()}\n\n"
        f"{role_instruction}\n\n"
        f"{base}\n\n"
        "If you are not sure about what you see, please say so rather than guessing. "
        "If the image quality or content is insufficient for assessment, state explicitly "
        "that you cannot assess it and explain what is missing or how to improve the image(s). "
        f"{language_instruction}"
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


def _run_analysis(role: str, images: List[PILImage.Image]) -> str:
    """Run the medical imaging agent for the given role and images, returning the text response."""
    agno_images: List[AgnoImage] = []

    for pil_image in images:
        image_bytes = _pil_to_bytes(pil_image)
        agno_images.append(AgnoImage(content=image_bytes, format="png"))

    prompt = _build_analysis_prompt(
        st.session_state.additional_info,
        role,
        st.session_state.user_language,
    )
    agent = _get_or_create_agent()
    response = agent.run(prompt, images=agno_images)
    analysis_text = _extract_response_text(response)

    st.session_state["analysis_model"] = get_default_model_id()
    st.session_state["analysis_context"] = st.session_state.additional_info
    st.session_state["analysis_results"][role] = analysis_text
    return analysis_text


def _render_image_gallery() -> None:
    """Render thumbnails of the current session gallery with delete buttons."""
    images = st.session_state.analysis_images
    if not images:
        return

    st.markdown("**Selected images**")
    cols = st.columns(min(len(images), 4))
    for idx, (col, item) in enumerate(zip(cols, images, strict=False)):
        with col:
            pil_image = PILImage.open(io.BytesIO(item["bytes"]))
            display = resize_for_display(pil_image, max_width=200)
            st.image(display, use_container_width=True)
            st.caption(item.get("caption", f"Image {idx + 1}"))
            if st.button("Remove", key=f"remove_image_{idx}", use_container_width=True):
                st.session_state.analysis_images.pop(idx)
                st.rerun()


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
                <li>EXIF/GPS metadata is stripped from smartphone photos before sending.</li>
                <li>Burned-in text/annotations inside the image pixels may still be visible.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Why is this required?"):
        st.write(
            "Medical images and health photos may contain protected health information. "
            "This confirmation helps ensure you do not accidentally send identifiable data "
            "to an external AI service."
        )
    return st.checkbox(
        "I confirm this upload and text contain no sensitive patient-identifying information",
        value=False,
        key="privacy_consent",
    )


def _render_photo_guidance() -> None:
    """Display tips for taking useful smartphone health photos."""
    st.info(
        "**Photo tips:** Use good, even lighting. Keep the camera steady and in focus. "
        "Include a coin or ruler as a scale if possible. Take one close-up and one overview photo. "
        "Use a plain, neutral background."
    )


def _render_privacy_options() -> None:
    """Render privacy toggles for EXIF stripping and optional face/tattoo blurring."""
    st.session_state.privacy_strip_exif = st.checkbox(
        "Remove EXIF/GPS metadata from photos before analysis",
        value=st.session_state.privacy_strip_exif,
        key="strip_exif_checkbox",
    )
    st.session_state.privacy_blur_faces = st.checkbox(
        "Blur faces and tattoos (experimental, local processing; requires opencv-python)",
        value=st.session_state.privacy_blur_faces,
        key="blur_faces_checkbox",
    )


def _render_prompt_templates() -> None:
    """Render selectable quick prompts and a custom context text area."""
    prompt_templates = {
        "Radiology-style report": (
            "Provide a radiology-style report with:\n"
            "- Modality and study type (if apparent)\n"
            "- Key findings\n"
            "- Impression (most likely diagnosis + differential)\n"
            "- Recommended next steps\n"
            "Keep it concise."
        ),
        "Explain for patient": "Explain the findings in simple, patient-friendly language.",
        "Focus: red flags": (
            "Focus on urgent findings / red flags and what to do next. "
            "For skin or nail photos, mention any signs that should be checked by a doctor soon."
        ),
        "Online research": (
            "Use online research (e.g., PubMed, medical journals, authoritative clinical references) "
            "to add evidence-based context, cite 2-3 sources, and include URLs where available."
        ),
        "Add patient context": (
            "Patient context:\n"
            "- Age: \n"
            "- Sex: \n"
            "- Symptoms: \n"
            "- Relevant history: \n"
            "- Clinical question: \n"
        ),
    }

    selected = st.multiselect(
        "Quick prompts (select one or more)",
        options=list(prompt_templates.keys()),
        default=st.session_state.selected_prompts,
        key="selected_prompts",
    )

    custom_context = st.text_area(
        "Additional context (e.g., patient history, symptoms)",
        value=st.session_state.get("custom_context", ""),
        placeholder="Enter any relevant information here...",
        key="custom_context_input",
        height=120,
    )
    st.session_state.custom_context = custom_context

    parts = [prompt_templates[label] for label in selected]
    if custom_context.strip():
        parts.append(custom_context.strip())
    st.session_state.additional_info = "\n\n".join(parts)
    st.caption(f"{len(st.session_state.additional_info)} characters")


def _render_anamnesis() -> None:
    """Render optional anamnesis fields."""
    anamnesis = st.session_state.get("photo_anamnesis", {})
    with st.expander("About this photo / Anamnese (optional)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            anamnesis["since_when"] = st.text_input(
                "Since when?", value=anamnesis.get("since_when", ""), key="anamnesis_since_when"
            )
            anamnesis["has_changed"] = st.text_input(
                "Has it changed?", value=anamnesis.get("has_changed", ""), key="anamnesis_changed"
            )
            anamnesis["size_approx"] = st.text_input(
                "Approximate size", value=anamnesis.get("size_approx", ""), key="anamnesis_size"
            )
        with col2:
            anamnesis["itching"] = st.text_input(
                "Itching?", value=anamnesis.get("itching", ""), key="anamnesis_itching"
            )
            anamnesis["bleeding"] = st.text_input(
                "Bleeding?", value=anamnesis.get("bleeding", ""), key="anamnesis_bleeding"
            )
            anamnesis["pain"] = st.text_input(
                "Pain?", value=anamnesis.get("pain", ""), key="anamnesis_pain"
            )
        anamnesis["additional_notes"] = st.text_area(
            "Additional notes",
            value=anamnesis.get("additional_notes", ""),
            key="anamnesis_notes",
            height=80,
        )
    st.session_state.photo_anamnesis = anamnesis


def _render_results(role: str) -> None:
    """Render parsed analysis results according to the selected role."""
    text = _get_analysis_text(role)
    if not text.strip():
        st.info("No analysis results available for this role yet.")
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


def _render_clinician_view(sections: Dict[str, str], raw_text: str) -> None:
    """Render a scannable clinician view of the report."""
    order = [
        "clinical interpretation",
        "professional analysis",
        "image technical assessment",
        "evidence-based context",
    ]
    for key in order:
        if key in sections:
            with st.expander(key.title(), expanded=True):
                st.markdown(sections[key])

    if "patient education" in sections:
        with st.expander("Patient Education", expanded=False):
            st.markdown(sections["patient education"])

    if "medical disclaimer" in sections:
        st.warning(sections["medical disclaimer"])

    if "_raw" in sections:
        only_raw = list(sections.keys()) == ["_raw"]
        with st.expander("Raw analysis", expanded=only_raw):
            st.markdown(sections["_raw"])
        st.caption(
            "Note: This analysis is generated by AI and should be reviewed by "
            "a qualified healthcare professional."
        )


def _render_patient_view(sections: Dict[str, str], raw_text: str) -> None:
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

    if "_raw" in sections:
        only_raw = list(sections.keys()) == ["_raw"]
        with st.expander("Full analysis", expanded=only_raw):
            st.markdown(sections["_raw"])


def _render_researcher_view(sections: Dict[str, str], raw_text: str) -> None:
    """Render the full structured report for researchers."""
    parsed_keys = [k for k in sections if k != "_raw"]
    for key, body in sections.items():
        if key == "_raw":
            continue
        with st.expander(key.title(), expanded=True):
            st.markdown(body)
    with st.expander("Raw response", expanded=not parsed_keys):
        st.markdown(raw_text)


def _render_export_and_feedback(role: str) -> None:
    """Render download buttons and a quick rating widget."""
    images = st.session_state.get("analysis_images", [])
    analysis_text = _get_analysis_text(role)
    model_id = st.session_state.get("analysis_model", get_default_model_id())
    additional_context = st.session_state.get("analysis_context", "")

    if not images or not analysis_text:
        return

    st.markdown("---")
    st.markdown("### Report actions")

    first_image_bytes = images[0]["bytes"]
    additional_image_bytes = [img["bytes"] for img in images[1:]] if len(images) > 1 else None

    md_content = cached_markdown_report(
        first_image_bytes,
        analysis_text,
        model_id,
        additional_context,
        additional_image_bytes=additional_image_bytes,
    )

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
                first_image_bytes,
                analysis_text,
                model_id,
                additional_context,
                additional_image_bytes=additional_image_bytes,
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
        subtitle="Upload medical images, health photos, or photographed documents",
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

        st.caption("Language")
        selected_language = st.radio(
            "Response language",
            options=["English", "Deutsch"],
            index=0 if st.session_state.user_language == "en" else 1,
            key="language_selector",
            label_visibility="collapsed",
        )
        st.session_state.user_language = "en" if selected_language == "English" else "de"

    upload_container = st.container()
    controls_container = st.container()
    analysis_container = st.container()

    # ----- Upload / camera section -----
    with upload_container:
        tab_upload, tab_camera = st.tabs(["Upload files", "Take photos"])

        with tab_upload:
            uploaded_files = st.file_uploader(
                "Upload image(s)",
                type=["jpg", "jpeg", "png", "dicom", "dcm"],
                accept_multiple_files=True,
                help="Supported formats: JPG, JPEG, PNG, DICOM, DCM. You can upload several files.",
                label_visibility="collapsed",
            )
            if uploaded_files:
                loaded = load_images(uploaded_files, anonymize=True)
                gallery_items = []
                for item in loaded:
                    fmt = (item.original_name or "").split(".")[-1].upper() or None
                    processed = _apply_privacy(item.pil_image, original_format=fmt)
                    gallery_items.append(
                        {
                            "bytes": _pil_to_bytes(processed),
                            "caption": item.original_name or "Uploaded image",
                            "source": item.source_type,
                        }
                    )
                _add_to_gallery(gallery_items)

        with tab_camera:
            _render_photo_guidance()
            camera_input = st.camera_input(
                "Take a photo",
                label_visibility="collapsed",
                key="camera_input",
            )
            if camera_input and st.button(
                "Add this photo to gallery", use_container_width=True, key="add_camera_photo"
            ):
                raw_loaded = load_camera_shot(camera_input.getvalue())
                processed = _apply_privacy(raw_loaded.pil_image)
                _add_to_gallery(
                    [
                        {
                            "bytes": _pil_to_bytes(processed),
                            "caption": "Camera capture",
                            "source": "camera",
                        }
                    ]
                )
                st.rerun()

    loaded_images = _gallery_to_loaded_images()

    if not loaded_images:
        empty_state(
            icon=":material/upload_file:",
            title="Upload or capture images to begin",
            description=(
                "Corpus Analyzer uses AI to provide educational explanations of medical images, "
                "smartphone health photos, and photographed documents."
            ),
        )
        workflow_steps()
        return

    try:
        for img in loaded_images:
            resize_for_display(img.pil_image)
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        st.info("Please upload valid JPG, PNG, or DICOM files and try again.")
        return

    with controls_container:
        _render_image_gallery()

        with st.expander("Image details", expanded=False):
            for idx, loaded in enumerate(loaded_images):
                fmt, dims = _image_detail_strings(loaded)
                st.write(f"**Image {idx + 1} — Format:** {fmt}, **Dimensions:** {dims}")
                if loaded.source_type == "dicom":
                    st.write("DICOM metadata was anonymized locally before conversion.")

        _render_privacy_options()
        safe_to_send = _render_consent()
        _render_anamnesis()
        _render_prompt_templates()

        analyze_button = st.button(
            "Analyze",
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
                    _run_analysis(
                        st.session_state.user_role, [img.pil_image for img in loaded_images]
                    )
                except Exception:
                    st.error(
                        "Sorry, we could not analyze the image(s). Please try again or contact support."
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
        elif any(_get_analysis_text(r) for r in ROLES):
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
                        _run_analysis(role, [img.pil_image for img in loaded_images])
                    except Exception:
                        st.error(
                            "Sorry, we could not analyze the image(s). Please try again or contact support."
                        )
                        st.info(
                            "If the problem persists, check that your OpenAI API key is valid "
                            "and has access to the selected model."
                        )
                        import logging

                        logging.getLogger(__name__).exception("Image analysis failed")
                        return
                st.rerun()


def _image_detail_strings(loaded: LoadedImage) -> tuple[str, str]:
    """Return (format, dimensions) strings for a loaded image."""
    if loaded.is_dicom:
        return "DICOM", f"{loaded.pil_image.size[0]} x {loaded.pil_image.size[1]} pixels"
    extension = (loaded.original_name or "").split(".")[-1].upper() or "Image"
    return extension, f"{loaded.pil_image.size[0]} x {loaded.pil_image.size[1]} pixels"


main()
