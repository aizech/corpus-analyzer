import datetime

import streamlit as st

from config import config

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="wide",
    menu_items=config.MENU_ITEMS,
)

pages = [
    st.Page(
        "views/Medical_Image_Analysis.py",
        title="Analyze",
        icon=":material/medical_services:",
    ),
    st.Page("views/Security.py", title="Security", icon=":material/security:"),
    st.Page("views/Feedback.py", title="Feedback", icon=":material/rate_review:"),
    st.Page("views/Configuration.py", title="Configuration", icon=":material/settings:"),
    st.Page("views/About.py", title="About", icon=":material/info:"),
]

page = st.navigation(pages)
page.run()

st.sidebar.markdown(" ")
st.sidebar.caption(
    f"© {datetime.date.today().year} | Made with :material/favorite: by [{config.COMPANY}]({config.COMPANY_URL})"
)
