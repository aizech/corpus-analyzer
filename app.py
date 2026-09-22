import datetime

import streamlit as st

from config import config
from translations import UI_TEXTS, _, get_language, set_language

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="wide",
    menu_items=config.MENU_ITEMS,
)

# Ensure a UI language is selected. Default to English.
if "ui_language" not in st.session_state:
    set_language("en")

with st.sidebar:
    st.caption(_("language_label"))
    selected_ui_language = st.radio(
        "UI language",
        options=["en", "de"],
        format_func=lambda lang: (
            UI_TEXTS["language_english"][lang]
            if lang == "en"
            else UI_TEXTS["language_german"][lang]
        ),
        index=0 if get_language() == "en" else 1,
        key="ui_language_selector",
        label_visibility="collapsed",
    )
    if selected_ui_language != get_language():
        set_language(selected_ui_language)
        st.rerun()

progress_page = st.Page(
    "views/Progress.py",
    title=_("page_progress"),
    icon=":material/history:",
)

pages = [
    st.Page(
        "views/Medical_Image_Analysis.py",
        title=_("page_analyze"),
        icon=":material/medical_services:",
    ),
    progress_page,
    st.Page("views/Security.py", title=_("page_security"), icon=":material/security:"),
    st.Page("views/Feedback.py", title=_("page_feedback"), icon=":material/rate_review:"),
    st.Page(
        "views/Configuration.py",
        title=_("page_configuration"),
        icon=":material/settings:",
    ),
    st.Page("views/About.py", title=_("page_about"), icon=":material/info:"),
]

page = st.navigation(pages)
page.run()

st.sidebar.markdown(" ")
st.sidebar.caption(
    f"© {datetime.date.today().year} | {_('footer_made_with')} :material/favorite: "
    f"{_('footer_by')} [{config.COMPANY}]({config.COMPANY_URL})"
)
