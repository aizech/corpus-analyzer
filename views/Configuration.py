import os

import streamlit as st

from models import MODEL_OPTIONS, get_default_model_key, set_default_model
from ui import card, render_page_header, section_header


def main():
    render_page_header(
        "Configuration",
        subtitle="System settings",
    )

    is_cloud = os.environ.get("STREAMLIT_RUNTIME_ENV") == "cloud"

    section_header("AI Model")
    current_default = get_default_model_key()
    selected_model_key = st.selectbox(
        "Select a model",
        options=list(MODEL_OPTIONS.keys()),
        index=(
            list(MODEL_OPTIONS.keys()).index(current_default)
            if current_default in MODEL_OPTIONS
            else 0
        ),
        key="model_selector_config",
    )
    st.caption(f"Current default: {MODEL_OPTIONS[selected_model_key]}")

    if st.button("Save Model Configuration", type="primary"):
        set_default_model(selected_model_key)
        st.session_state.medical_agent = None
        st.success(f"Default model set to {selected_model_key}")

    section_header("API Key")
    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}

    if is_cloud:
        st.warning(
            "You're running this app online. Please enter your own API key below. "
            "This key will be stored in your session and won't be saved permanently."
        )
        default_key = st.session_state.api_keys.get("OPENAI_API_KEY", "")
        openai_api_key = st.text_input(
            "Enter your OpenAI API Key",
            value=default_key,
            type="password",
            help="Your OpenAI API key for accessing GPT models",
        )
        if openai_api_key:
            st.session_state.api_keys["OPENAI_API_KEY"] = openai_api_key
            os.environ["OPENAI_API_KEY"] = openai_api_key
            if st.button("Apply API Key"):
                st.success("API Key applied for this session!")
        else:
            st.warning("Please enter your OpenAI API key to use this application.")
    else:
        card(
            title="BETA mode active",
            content="No API key is required yet — this project is currently sponsored. "
            "If you want to use your own key, set ``OPENAI_API_KEY`` in your environment.",
            icon="✅",
        )

    section_header("Web Fetcher")
    web_fetcher_enabled = os.environ.get("ENABLE_WEB_FETCHER", "true").lower() in (
        "true",
        "1",
        "yes",
    )
    if web_fetcher_enabled:
        st.success(
            "Web fetcher is enabled. The medical agent can retrieve web pages and literature."
        )
    else:
        st.info("Web fetcher is disabled. Set ``ENABLE_WEB_FETCHER=true`` to enable it.")


main()
