import io
from typing import Dict, List, Optional

import streamlit as st
from agno.media import Image as AgnoImage
from PIL import Image as PILImage

from agents.medical_agent import create_medical_imaging_agent
from analysis_format import confidence_level, parse_analysis_sections
from analysis_prompt import build_analysis_prompt, build_anamnesis_text
from config import config
from export import PDF_EXPORT_AVAILABLE, cached_markdown_report, cached_pdf_report
from image_loader import LoadedImage, load_camera_shot, load_images, resize_for_display
from models import get_default_model_id
from photo_privacy import blur_faces_and_tattoos, is_opencv_available, strip_exif
from translations import format_text
from ui import (
    card,
    empty_state,
    inject_custom_css,
    render_page_header,
    render_sidebar_info,
    role_badge,
    workflow_steps,
)

ROLES = ["clinician", "patient", "researcher"]


def _init_session() -> None:
    """Initialize session state keys used by this page."""
    defaults: Dict[str, object] = {
        "user_role": "clinician",
        "user_language": st.session_state.get("ui_language", "en"),
        "additional_info": "",
        "analysis_results": {},
        "analysis_images": [],  # list of {"bytes": bytes, "caption": str, "source": str}
        "analysis_model": "",
        "analysis_context": "",
        "photo_anamnesis": {},
        "privacy_strip_exif": True,
        "privacy_blur_faces": False,
        "progress_tracking_consent": False,
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
                {
                    "bytes": legacy_bytes,
                    "caption": format_text("uploaded_image"),
                    "source": "upload",
                }
            ]

    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Keep response language in sync with the global UI language.
    st.session_state.user_language = st.session_state.get("ui_language", "en")


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


def _build_analysis_prompt(additional_info: str, role: str, language: str) -> str:
    """Build the prompt sent to the medical imaging agent."""
    anamnesis = st.session_state.get("photo_anamnesis", {})
    translated_labels = {
        "since_when": format_text("anamnesis_since_when"),
        "has_changed": format_text("anamnesis_changed"),
        "itching": format_text("anamnesis_itching"),
        "bleeding": format_text("anamnesis_bleeding"),
        "pain": format_text("anamnesis_pain"),
        "size_approx": format_text("anamnesis_size"),
        "additional_notes": format_text("anamnesis_notes"),
    }
    anamnesis_text = build_anamnesis_text(
        anamnesis,
        label=format_text("anamnesis_label"),
        labels=translated_labels,
    )
    return build_analysis_prompt(
        additional_info=additional_info,
        role=role,
        language=language,
        anamnesis_text=anamnesis_text,
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

    st.markdown(f"**{format_text('selected_images')}**")
    cols = st.columns(min(len(images), 4))
    for idx, (col, item) in enumerate(zip(cols, images, strict=False)):
        with col:
            pil_image = PILImage.open(io.BytesIO(item["bytes"]))
            display = resize_for_display(pil_image, max_width=200)
            st.image(display, use_container_width=True)
            st.caption(item.get("caption", f"{format_text('uploaded_image')} {idx + 1}"))
            if st.button(
                format_text("remove"), key=f"remove_image_{idx}", use_container_width=True
            ):
                st.session_state.analysis_images.pop(idx)
                st.rerun()


def _render_consent() -> bool:
    """Render the privacy consent panel and return whether it is checked."""
    st.markdown(
        f"""
        <div class="ca-consent">
            <div class="ca-consent-title">{format_text("consent_title")}</div>
            <div style="margin-bottom: 0.5rem;">{format_text("consent_intro")}</div>
            <ul class="ca-consent-list">
                <li>{format_text("consent_item_1")}</li>
                <li>{format_text("consent_item_2")}</li>
                <li>{format_text("consent_item_3")}</li>
                <li>{format_text("consent_item_4")}</li>
                <li>{format_text("consent_item_5")}</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander(format_text("consent_why_title")):
        st.write(format_text("consent_why_text"))
    return st.checkbox(
        format_text("consent_checkbox"),
        value=False,
        key="privacy_consent",
    )


def _render_photo_guidance() -> None:
    """Display tips for taking useful smartphone health photos."""
    st.info(format_text("photo_tips"))


def _render_privacy_options() -> None:
    """Render privacy toggles for EXIF stripping and optional face/tattoo blurring."""
    st.session_state.privacy_strip_exif = st.checkbox(
        format_text("privacy_strip_exif"),
        value=st.session_state.privacy_strip_exif,
        key="strip_exif_checkbox",
    )
    blur_available = is_opencv_available()
    st.session_state.privacy_blur_faces = st.checkbox(
        format_text("privacy_blur_faces"),
        value=st.session_state.privacy_blur_faces,
        key="blur_faces_checkbox",
        disabled=not blur_available,
    )
    if not blur_available:
        st.caption(format_text("privacy_blur_unavailable"))


def _render_progress_tracking_consent() -> bool:
    """Render the separate, explicit consent for progress tracking.

    Returns whether progress tracking is consented. If the feature flag is
    disabled, this always returns False so no snapshot UI is offered.
    """
    if not config.ENABLE_PROGRESS_TRACKING:
        st.session_state.progress_tracking_consent = False
        return False

    st.markdown(f"**{format_text('progress_tracking_consent_title')}**")
    st.markdown(format_text("progress_tracking_consent_text"))
    st.session_state.progress_tracking_consent = st.checkbox(
        format_text("progress_tracking_consent_checkbox"),
        value=st.session_state.progress_tracking_consent,
        key="progress_tracking_consent_checkbox",
    )
    return st.session_state.progress_tracking_consent


def _render_prompt_templates() -> None:
    """Render selectable quick prompts and a custom context text area."""
    prompt_templates = {
        format_text("quick_prompt_radiology"): (
            "Provide a radiology-style report with:\n"
            "- Modality and study type (if apparent)\n"
            "- Key findings\n"
            "- Impression (most likely diagnosis + differential)\n"
            "- Recommended next steps\n"
            "Keep it concise."
        ),
        format_text(
            "quick_prompt_patient"
        ): "Explain the findings in simple, patient-friendly language.",
        format_text("quick_prompt_redflags"): (
            "Focus on urgent findings / red flags and what to do next. "
            "For skin or nail photos, mention any signs that should be checked by a doctor soon."
        ),
        format_text("quick_prompt_research"): (
            "Use online research (e.g., PubMed, medical journals, authoritative clinical references) "
            "to add evidence-based context, cite 2-3 sources, and include URLs where available."
        ),
        format_text("quick_prompt_context"): (
            "Patient context:\n"
            "- Age: \n"
            "- Sex: \n"
            "- Symptoms: \n"
            "- Relevant history: \n"
            "- Clinical question: \n"
        ),
    }

    selected = st.multiselect(
        format_text("quick_prompts_label"),
        options=list(prompt_templates.keys()),
        default=st.session_state.selected_prompts,
        key="selected_prompts",
    )

    custom_context = st.text_area(
        format_text("additional_context_label"),
        value=st.session_state.get("custom_context", ""),
        placeholder=format_text("additional_context_placeholder"),
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
    with st.expander(
        f"{format_text('anamnesis_title')} ({format_text('optional')})", expanded=False
    ):
        col1, col2 = st.columns(2)
        with col1:
            anamnesis["since_when"] = st.text_input(
                format_text("anamnesis_since_when"),
                value=anamnesis.get("since_when", ""),
                key="anamnesis_since_when",
            )
            anamnesis["has_changed"] = st.text_input(
                format_text("anamnesis_changed"),
                value=anamnesis.get("has_changed", ""),
                key="anamnesis_changed",
            )
            anamnesis["size_approx"] = st.text_input(
                format_text("anamnesis_size"),
                value=anamnesis.get("size_approx", ""),
                key="anamnesis_size",
            )
        with col2:
            anamnesis["itching"] = st.text_input(
                format_text("anamnesis_itching"),
                value=anamnesis.get("itching", ""),
                key="anamnesis_itching",
            )
            anamnesis["bleeding"] = st.text_input(
                format_text("anamnesis_bleeding"),
                value=anamnesis.get("bleeding", ""),
                key="anamnesis_bleeding",
            )
            anamnesis["pain"] = st.text_input(
                format_text("anamnesis_pain"),
                value=anamnesis.get("pain", ""),
                key="anamnesis_pain",
            )
        anamnesis["additional_notes"] = st.text_area(
            format_text("anamnesis_notes"),
            value=anamnesis.get("additional_notes", ""),
            key="anamnesis_notes",
            height=80,
        )
    st.session_state.photo_anamnesis = anamnesis


def _render_results(role: str) -> None:
    """Render parsed analysis results according to the selected role."""
    text = _get_analysis_text(role)
    if not text.strip():
        st.info(format_text("no_results_for_role"))
        return

    sections = parse_analysis_sections(text)
    confidence = confidence_level(text)

    st.markdown(f"## :material/medical_services: {format_text('analysis_results_title')}")
    col1, col2 = st.columns([1, 6])
    with col1:
        role_badge(role)
    with col2:
        if confidence:
            badge_class = f"ca-badge-confidence-{confidence}"
            st.markdown(
                f'<span class="ca-badge {badge_class}">{format_text("confidence_label")}: {confidence.capitalize()}</span>',
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
        with st.expander(format_text("patient_education"), expanded=False):
            st.markdown(sections["patient education"])

    if "medical disclaimer" in sections:
        st.warning(sections["medical disclaimer"])

    if "_raw" in sections:
        only_raw = list(sections.keys()) == ["_raw"]
        with st.expander(format_text("raw_analysis"), expanded=only_raw):
            st.markdown(sections["_raw"])
        st.caption(format_text("ai_review_note"))


def _render_patient_view(sections: Dict[str, str], raw_text: str) -> None:
    """Render a simplified patient-friendly view."""
    if "patient education" in sections:
        card(
            format_text("patient_education"), sections["patient education"], icon=":material/info:"
        )
    elif "clinical interpretation" in sections:
        card(
            format_text("patient_education"),
            sections["clinical interpretation"],
            icon=":material/info:",
        )

    if "clinical interpretation" in sections and "patient education" in sections:
        with st.expander(format_text("clinical_details"), expanded=False):
            st.markdown(sections["clinical interpretation"])

    if "medical disclaimer" in sections:
        st.warning(sections["medical disclaimer"])

    if "_raw" in sections:
        only_raw = list(sections.keys()) == ["_raw"]
        with st.expander(format_text("full_analysis"), expanded=only_raw):
            st.markdown(sections["_raw"])


def _render_researcher_view(sections: Dict[str, str], raw_text: str) -> None:
    """Render the full structured report for researchers."""
    parsed_keys = [k for k in sections if k != "_raw"]
    for key, body in sections.items():
        if key == "_raw":
            continue
        with st.expander(key.title(), expanded=True):
            st.markdown(body)
    with st.expander(format_text("raw_response"), expanded=not parsed_keys):
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
    st.markdown(f"### {format_text('report_actions_title')}")

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
            label=format_text("download_markdown"),
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
                label=format_text("download_pdf"),
                icon=":material/download:",
                data=pdf_content,
                file_name="corpus_analyzer_analysis.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.caption(format_text("pdf_disabled"))
    with col3:
        st.feedback("stars", key="analysis_rating")


def main() -> None:
    inject_custom_css()
    render_page_header(
        format_text("analyze_title"),
        subtitle=format_text("analyze_subtitle"),
    )
    render_sidebar_info()
    _init_session()

    with st.sidebar:
        st.markdown("---")
        st.caption(format_text("user_mode_label"))
        role_labels = {
            "clinician": format_text("role_clinician"),
            "patient": format_text("role_patient"),
            "researcher": format_text("role_researcher"),
        }
        selected_role = st.radio(
            format_text("view_results_as"),
            options=ROLES,
            format_func=lambda r: role_labels[r],
            index=ROLES.index(st.session_state.user_role),
            key="role_selector",
        )
        st.session_state.user_role = selected_role.lower()

    upload_container = st.container()
    controls_container = st.container()
    analysis_container = st.container()

    # ----- Upload / camera section -----
    with upload_container:
        tab_upload, tab_camera = st.tabs([format_text("tab_upload"), format_text("tab_camera")])

        with tab_upload:
            uploaded_files = st.file_uploader(
                format_text("upload_label"),
                type=["jpg", "jpeg", "png", "dicom", "dcm"],
                accept_multiple_files=True,
                help=format_text("upload_help"),
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
                            "caption": item.original_name or format_text("uploaded_image"),
                            "source": item.source_type,
                        }
                    )
                _add_to_gallery(gallery_items)

        with tab_camera:
            _render_photo_guidance()
            camera_input = st.camera_input(
                format_text("camera_label"),
                label_visibility="collapsed",
                key="camera_input",
            )
            if camera_input and st.button(
                format_text("add_photo_button"),
                use_container_width=True,
                key="add_camera_photo",
            ):
                raw_loaded = load_camera_shot(camera_input.getvalue())
                processed = _apply_privacy(raw_loaded.pil_image)
                _add_to_gallery(
                    [
                        {
                            "bytes": _pil_to_bytes(processed),
                            "caption": format_text("camera_capture"),
                            "source": "camera",
                        }
                    ]
                )
                st.rerun()

    loaded_images = _gallery_to_loaded_images()

    if not loaded_images:
        empty_state(
            icon=":material/upload_file:",
            title=format_text("empty_state_title"),
            description=format_text("empty_state_description"),
        )
        workflow_steps()
        return

    try:
        for img in loaded_images:
            resize_for_display(img.pil_image)
    except Exception as e:
        st.error(f"{format_text('analysis_error')}: {str(e)}")
        st.info(format_text("api_key_error"))
        return

    with controls_container:
        _render_image_gallery()

        with st.expander(format_text("image_details"), expanded=False):
            for idx, loaded in enumerate(loaded_images):
                fmt, dims = _image_detail_strings(loaded)
                st.write(
                    f"**{format_text('uploaded_image')} {idx + 1} — {format_text('format')}:** {fmt}, "
                    f"**{format_text('dimensions')}:** {dims}"
                )
                if loaded.source_type == "dicom":
                    st.write(format_text("dicom_anonymized_note"))

        _render_privacy_options()
        safe_to_send = _render_consent()
        _render_progress_tracking_consent()
        _render_anamnesis()
        _render_prompt_templates()

        analyze_button = st.button(
            format_text("analyze"),
            icon=":material/search:",
            type="primary",
            use_container_width=True,
            disabled=not safe_to_send,
        )

    with analysis_container:
        if analyze_button:
            if not safe_to_send:
                st.error(format_text("consent_missing_error"))
                return

            with st.spinner(format_text("analysis_spinner")):
                try:
                    _run_analysis(
                        st.session_state.user_role, [img.pil_image for img in loaded_images]
                    )
                except Exception:
                    st.error(format_text("analysis_error"))
                    st.info(format_text("api_key_error"))
                    import logging

                    logging.getLogger(__name__).exception("Image analysis failed")
                    return

        role = st.session_state.user_role
        if _get_analysis_text(role):
            _render_results(role)
        elif any(_get_analysis_text(r) for r in ROLES):
            st.info(format_text("role_switch_info", role=role_labels[role]))
            if st.button(
                format_text("reanalyze_as", role=role_labels[role]),
                icon=":material/refresh:",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner(format_text("analysis_spinner")):
                    try:
                        _run_analysis(role, [img.pil_image for img in loaded_images])
                    except Exception:
                        st.error(format_text("analysis_error"))
                        st.info(format_text("api_key_error"))
                        import logging

                        logging.getLogger(__name__).exception("Image analysis failed")
                        return
                st.rerun()


def _image_detail_strings(loaded: LoadedImage) -> tuple[str, str]:
    """Return (format, dimensions) strings for a loaded image."""
    if loaded.is_dicom:
        return "DICOM", f"{loaded.pil_image.size[0]} x {loaded.pil_image.size[1]} pixels"
    extension = (loaded.original_name or "").split(".")[-1].upper() or format_text("uploaded_image")
    return extension, f"{loaded.pil_image.size[0]} x {loaded.pil_image.size[1]} pixels"


main()
