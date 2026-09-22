import os

import streamlit as st

from models import MODEL_OPTIONS, get_default_model_key, set_default_model
from translations import format_text
from ui import card, render_page_header, section_header


def main():
    render_page_header(
        format_text("configuration_title"),
        subtitle=format_text("configuration_subtitle"),
    )

    is_cloud = os.environ.get("STREAMLIT_RUNTIME_ENV") == "cloud"

    section_header(format_text("config_model_section"))
    current_default = get_default_model_key()
    selected_model_key = st.selectbox(
        format_text("config_select_model"),
        options=list(MODEL_OPTIONS.keys()),
        index=(
            list(MODEL_OPTIONS.keys()).index(current_default)
            if current_default in MODEL_OPTIONS
            else 0
        ),
        key="model_selector_config",
    )
    st.caption(f"{format_text('config_select_model')}: {MODEL_OPTIONS[selected_model_key]}")

    if st.button(format_text("config_save_model"), type="primary"):
        set_default_model(selected_model_key)
        st.session_state.medical_agent = None
        st.success(format_text("config_model_saved", model=selected_model_key))

    section_header(format_text("config_api_key_section"))
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}

    if is_cloud:
        st.warning(format_text("config_cloud_warning"))
        default_key = st.session_state.api_keys.get("OPENAI_API_KEY", "")
        openai_api_key = st.text_input(
            format_text("config_api_key_input"),
            value=default_key,
            type="password",
            help=format_text("config_api_key_help"),
        )
        if openai_api_key:
            st.session_state.api_keys["OPENAI_API_KEY"] = openai_api_key
            os.environ["OPENAI_API_KEY"] = openai_api_key
            if st.button(format_text("save")):
                st.success(format_text("config_api_key_applied"))
        else:
            st.warning(format_text("config_api_key_missing"))
    else:
        card(
            title=format_text("config_beta_active"),
            content=format_text("config_beta_text"),
            icon=":material/verified:",
        )

    section_header(format_text("config_web_fetcher_section"))
    web_fetcher_enabled = os.environ.get("ENABLE_WEB_FETCHER", "true").lower() in (
        "true",
        "1",
        "yes",
    )
    if web_fetcher_enabled:
        st.success(format_text("config_web_fetcher_enabled"))
    else:
        st.info(format_text("config_web_fetcher_disabled"))


main()
