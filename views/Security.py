import streamlit as st

from ui import render_page_header


def main():
    render_page_header(
        "Security",
        subtitle="Security & Privacy",
        page_icon="material/security",
    )

    st.markdown("""
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
- We are using OpenAI models via the OpenAI API, OpenAI provides documentation about how API data is handled:
- https://platform.openai.com/docs/guides/your-data

In general, OpenAI states that:

- API inputs/outputs are **not used to train** OpenAI models **by default** and we do NOT explicitly opt in, so your data is not used.
- OpenAI retains certain request/response data for **abuse monitoring and safety** purposes for 30 days. Then all data is deleted completely.

Always verify the current policy details in the official link above, since policies can change.

## Contact

If you have security questions or want to report a vulnerability, contact:

- **Email**: `support@corpusanalytica.com`
""")


main()
