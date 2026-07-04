import os

import streamlit as st

from models import MODEL_OPTIONS, get_default_model_key, set_default_model
from ui import render_page_header


def main():
    render_page_header(
        "Configuration",
        subtitle="System settings",
        page_icon="material/settings",
    )

    tab1, tab2 = st.tabs([":material/tune: Models", ":material/key: API Keys"])

    with tab1:
        st.subheader("Default AI Model")
        st.write(
            "Select the default model to use across the application. This model will be used for all sessions."
        )

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

        st.caption(f"Current default: {current_default}")

        if st.button("Save Model Configuration", type="primary"):
            set_default_model(selected_model_key)
            st.session_state.medical_agent = None
            st.success(f"Default model set to {selected_model_key}")

    with tab2:
        is_cloud = os.environ.get("STREAMLIT_RUNTIME_ENV") == "cloud"

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
            st.info("This app is in BETA. We sponsor this project. So no API Key is needed yet.")


main()
