"""Progress tracking view: compare saved snapshots over time."""

import io
from typing import List
from uuid import uuid4

import streamlit as st
from PIL import Image as PILImage

from agents.medical_agent import create_medical_imaging_agent
from analysis_format import confidence_level, parse_analysis_sections
from config import config
from models import get_default_model_id
from progress_prompt import build_comparison_prompt
from storage.factory import get_storage_backend
from storage.models import PhotoSnapshot
from translations import format_text
from ui import empty_state, render_page_header, section_header
from ui.body_map import BODY_SITE_OPTIONS, body_site_label


def _init_session() -> None:
    """Initialize session state keys used by this page."""
    if "progress_user_id" not in st.session_state:
        st.session_state.progress_user_id = str(uuid4())
    if "comparison_result" not in st.session_state:
        st.session_state.comparison_result = ""


def _pil_from_bytes(image_bytes: bytes) -> PILImage.Image:
    return PILImage.open(io.BytesIO(image_bytes))


def _render_snapshot_card(snapshot: PhotoSnapshot, idx: int) -> None:
    st.markdown(f"**{idx}. {body_site_label(snapshot.body_site or '')}**")
    if snapshot.encrypted_image:
        st.image(_pil_from_bytes(snapshot.encrypted_image), use_container_width=True)
    st.caption(snapshot.created_at.strftime("%Y-%m-%d %H:%M"))
    if snapshot.analysis_summary:
        with st.expander(format_text("snapshot_summary"), expanded=False):
            st.markdown(snapshot.analysis_summary)


def _run_comparison(earlier: PhotoSnapshot, later: PhotoSnapshot, role: str, language: str) -> str:
    """Run the agent to compare two snapshots."""
    from agno.media import Image as AgnoImage

    images: List[AgnoImage] = []
    for snapshot in (earlier, later):
        if snapshot.encrypted_image:
            images.append(AgnoImage(content=snapshot.encrypted_image, format="png"))

    prompt = build_comparison_prompt(earlier, later, role=role, language=language)
    agent = create_medical_imaging_agent(model_id=get_default_model_id())
    response = agent.run(prompt, images=images)

    if hasattr(response, "content"):
        return str(response.content)
    if isinstance(response, str):
        return response
    if isinstance(response, dict) and "content" in response:
        return str(response["content"])
    return str(response)


def _render_results(text: str) -> None:
    sections = parse_analysis_sections(text)
    confidence = confidence_level(text)

    st.markdown(f"## {format_text('comparison_results_title')}")
    if confidence:
        st.markdown(
            f'<span class="ca-badge">{format_text("confidence_label")}: {confidence.capitalize()}</span>',
            unsafe_allow_html=True,
        )

    for key, body in sections.items():
        if key == "_raw":
            continue
        with st.expander(key.title(), expanded=True):
            st.markdown(body)

    if "_raw" in sections:
        only_raw = list(sections.keys()) == ["_raw"]
        with st.expander(format_text("raw_analysis"), expanded=only_raw):
            st.markdown(sections["_raw"])

    st.warning(format_text("ai_review_note"))


def main() -> None:
    render_page_header(
        format_text("progress_title"),
        subtitle=format_text("progress_subtitle"),
    )
    _init_session()

    if not config.ENABLE_PROGRESS_TRACKING:
        st.info(format_text("progress_disabled"))
        return

    user_id = st.session_state.progress_user_id
    try:
        backend = get_storage_backend()
    except Exception as e:
        st.error(format_text("progress_storage_error"))
        st.exception(e)
        return

    section_header(format_text("progress_select_site"))
    selected_site = st.selectbox(
        format_text("body_site_label"),
        options=list(BODY_SITE_OPTIONS.keys()),
        format_func=lambda key: body_site_label(key),
        key="progress_site_selector",
    )

    snapshots = backend.list_snapshots(user_id, body_site=selected_site)
    if len(snapshots) < 2:
        empty_state(
            icon=":material/history:",
            title=format_text("progress_not_enough_title"),
            description=format_text("progress_not_enough_description"),
        )
        return

    section_header(format_text("progress_select_snapshots"))
    st.markdown(format_text("progress_select_two"))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{format_text('progress_earlier')}**")
        earlier_index = st.selectbox(
            format_text("progress_earlier"),
            options=list(range(len(snapshots))),
            format_func=lambda i: snapshots[i].created_at.strftime("%Y-%m-%d %H:%M"),
            key="earlier_snapshot",
            label_visibility="collapsed",
        )
        _render_snapshot_card(snapshots[earlier_index], 1)

    with col2:
        st.markdown(f"**{format_text('progress_later')}**")
        later_index = st.selectbox(
            format_text("progress_later"),
            options=list(range(len(snapshots))),
            format_func=lambda i: snapshots[i].created_at.strftime("%Y-%m-%d %H:%M"),
            key="later_snapshot",
            label_visibility="collapsed",
        )
        _render_snapshot_card(snapshots[later_index], 2)

    if earlier_index == later_index:
        st.warning(format_text("progress_same_snapshot"))
        return

    earlier = snapshots[earlier_index]
    later = snapshots[later_index]
    # Ensure earlier is actually the older one.
    if later.created_at < earlier.created_at:
        earlier, later = later, earlier

    role = st.session_state.get("user_role", "patient")
    language = st.session_state.get("ui_language", "en")

    if st.button(format_text("progress_compare"), type="primary", use_container_width=True):
        with st.spinner(format_text("analysis_spinner")):
            try:
                result = _run_comparison(earlier, later, role=role, language=language)
                st.session_state.comparison_result = result
            except Exception as e:
                st.error(format_text("analysis_error"))
                st.exception(e)
                return
        st.rerun()

    if st.session_state.comparison_result:
        _render_results(st.session_state.comparison_result)


main()
