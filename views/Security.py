import streamlit as st

from config import config
from translations import format_text
from ui import card, render_page_header, section_header


def main():
    render_page_header(
        format_text("security_title"),
        subtitle=format_text("security_subtitle"),
    )

    section_header(format_text("security_how_data_handled"))

    card(
        title=format_text("security_upload_title"),
        content=format_text("security_upload_text"),
        icon=":material/upload:",
    )
    card(
        title=format_text("security_dicom_title"),
        content=format_text("security_dicom_text"),
        icon=":material/shield:",
    )
    card(
        title=format_text("security_photo_title"),
        content=format_text("security_photo_text"),
        icon=":material/photo_camera:",
    )
    card(
        title=format_text("security_sent_title"),
        content=format_text("security_sent_text"),
        icon=":material/send:",
    )
    card(
        title=format_text("security_not_stored_title"),
        content=format_text("security_not_stored_text"),
        icon=":material/delete_forever:",
    )

    section_header(format_text("security_law_title"))
    st.markdown(format_text("security_law_text"))

    section_header(format_text("security_retention_title"))
    st.markdown(format_text("security_retention_text"))
    st.link_button(
        format_text("security_openai_button"),
        "https://platform.openai.com/docs/guides/your-data",
    )

    section_header(format_text("security_contact"))
    st.markdown(format_text("security_contact_text", email=config.CONTACT_EMAIL))


main()
