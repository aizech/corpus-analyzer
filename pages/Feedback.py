import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage

import streamlit as st

from config import config

# Page config
st.set_page_config(
    page_title=f"{config.APP_NAME} - Feedback",
    page_icon=config.APP_ICON,
    layout="wide",
    #initial_sidebar_state="collapsed",
    menu_items=config.MENU_ITEMS
)

# Logo in sidebar
st.logo(config.LOGO_TEXT_PATH,
    size="large",
    icon_image=config.LOGO_ICON_PATH
)

# Page title
one_cola = st.columns([1])[0]
with one_cola:
    col1a, col2a = st.columns([1, 5])

    with col1a:
        #team_image = config.LOGO_TEAM_PATH
        st.image(config.LOGO_TEAM_PATH, width=100)
        #st.image(team_image, width=400)
    with col2a:
        st.markdown("""
        # Corpus Analyzer 
        ## Feedback
        """, unsafe_allow_html=True)


def _get_secret(name: str, default: str | None = None) -> str | None:
    try:
        if name in st.secrets:
            value = st.secrets.get(name)
            if value is not None and str(value).strip() != "":
                return str(value)
    except Exception:
        pass

    value = os.environ.get(name)
    if value is not None and value.strip() != "":
        return value

    return default


def _send_feedback_email(
    *,
    rating: int,
    feedback: str,
    name: str | None,
    email: str | None,
) -> None:
    smtp_host = _get_secret("SMTP_HOST")
    smtp_port_str = _get_secret("SMTP_PORT", "587")
    smtp_username = _get_secret("SMTP_USERNAME")
    smtp_password = _get_secret("SMTP_PASSWORD")

    smtp_from = _get_secret("SMTP_FROM", config.CONTACT_EMAIL)
    smtp_to = _get_secret("SMTP_TO", config.CONTACT_EMAIL)

    if not smtp_host or not smtp_port_str or not smtp_from or not smtp_to:
        raise RuntimeError(
            "Missing SMTP configuration. Please set SMTP_HOST, SMTP_PORT, SMTP_FROM, SMTP_TO (and optionally SMTP_USERNAME/SMTP_PASSWORD)."
        )

    try:
        smtp_port = int(smtp_port_str)
    except ValueError as e:
        raise RuntimeError("SMTP_PORT must be an integer") from e

    use_tls_raw = _get_secret("SMTP_USE_TLS", "true")
    use_tls = str(use_tls_raw).strip().lower() in {"1", "true", "yes", "y"}

    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    msg = EmailMessage()
    msg["Subject"] = f"{config.APP_NAME} Feedback: {rating}/5"
    msg["From"] = smtp_from
    msg["To"] = smtp_to

    lines: list[str] = []
    lines.append(f"App: {config.APP_NAME}")
    lines.append(f"Rating: {rating}/5")
    lines.append(f"Submitted: {now}")
    lines.append("")
    lines.append("Feedback:")
    lines.append(feedback.strip())
    lines.append("")
    lines.append("Optional user info:")
    lines.append(f"Name: {name.strip() if name else ''}")
    lines.append(f"Email: {email.strip() if email else ''}")

    msg.set_content("\n".join(lines))

    if use_tls:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP_SSL(
            smtp_host, smtp_port, timeout=20, context=ssl.create_default_context()
        ) as server:
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(msg)


def main() -> None:
    #st.title("Feedback")

    repo_url = _get_secret("GITHUB_REPO_URL", config.GITHUB_REPO_URL)

    st.subheader("Report bugs / request features")

    if repo_url:
        bug_url = f"{repo_url.rstrip('/')}/issues/new?template=bug_report.yml"
        feature_url = f"{repo_url.rstrip('/')}/issues/new?template=feature_request.yml"
        st.markdown(
            f"- **Bug report**: [{bug_url}]({bug_url})\n"
            f"- **Feature request**: [{feature_url}]({feature_url})"
        )
    else:
        st.info(
            "GitHub links are not configured. Set the environment variable `GITHUB_REPO_URL` "
            "(e.g. https://github.com/<org>/<repo>) to enable one-click issue links."
        )

    st.divider()
    st.subheader("Rate the app")

    with st.form("feedback_form"):
        rating_selected = st.feedback(
            "stars",
            key="feedback_rating",
            default=4,
            width="content",
        )
        rating = (rating_selected + 1) if rating_selected is not None else 5

        feedback = st.text_area(
            "Your feedback",
            placeholder="What worked well? What should be improved?",
            height=220,
        )

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name (optional)")
        with col2:
            email = st.text_input("Email address (optional)")

        submitted = st.form_submit_button("Send feedback", type="primary")

    if submitted:
        if not feedback.strip():
            st.error("Please enter some feedback before sending.")
            return

        try:
            _send_feedback_email(
                rating=int(rating),
                feedback=feedback,
                name=name,
                email=email,
            )
        except Exception as e:
            st.error(
                "Could not send feedback email. Please check SMTP settings (SMTP_HOST, SMTP_PORT, SMTP_FROM, SMTP_TO, SMTP_USERNAME, SMTP_PASSWORD, SMTP_USE_TLS)."
            )
            st.exception(e)
            return

        st.success("Thanks — your feedback was sent!")


if __name__ == "__main__":
    main()
