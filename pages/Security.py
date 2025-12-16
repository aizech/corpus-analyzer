import streamlit as st

from config import config


# Page config
st.set_page_config(
    page_title=f"{config.APP_NAME} - Security",
    page_icon=":material/security:",
    layout="wide",
    menu_items=config.MENU_ITEMS,
)

# Logo in sidebar
st.logo(
    config.LOGO_TEXT_PATH,
    size="large",
    icon_image=config.LOGO_ICON_PATH,
)

# Page title
one_cola = st.columns([1])[0]
with one_cola:
    col1a, col2a = st.columns([1, 5])

    with col1a:
        st.image(config.LOGO_TEAM_PATH, width=100)
    with col2a:
        st.markdown(
            """
        # Corpus Analyzer 
        ## Security & Privacy
        """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
## Summary

This page explains how Corpus Analyzer handles your inputs and what you can do to use the app safely.

## How images are handled

- **Upload (in-memory)**
  Uploaded images (JPG/PNG) and DICOM files are received via Streamlit's file uploader.

- **Temporary processing on disk**
  When you click **Analyze Image**, the app processes the image in memory and sends image bytes directly.

- **DICOM processing and metadata**
  If you upload a DICOM (`.dcm`/`.dicom`), the app reads pixel data to create a preview image.
  The app does **not** include DICOM metadata in the prompt.

- **Local DICOM anonymization**
  The app clears common identifying DICOM tags locally before analysis. This does not remove burned-in annotations in pixel data, if there are any.

## Where your data is sent

The app sends:

- Your **prompt text** (including any additional context you type)
- The **image bytes**

Before the request is made, the app asks you to confirm that your upload and text contain no sensitive patient-identifying information.

…to the configured AI model provider (for example, an OpenAI model) in order to generate an analysis.

## Data retention

- The app does not write your uploaded image to disk as part of analysis.
- Any retention by third-party model providers depends on their policies and your account configuration.

## Contact

If you have security questions or want to report a vulnerability, contact:

- **Email**: `support@corpusanalytica.com`
"""
)
