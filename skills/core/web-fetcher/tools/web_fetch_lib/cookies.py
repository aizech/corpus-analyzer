"""Cookie store for authenticated / login-gated fetches."""

from urllib.parse import urlparse

_cookie_store: dict[str, list[dict]] = {}


def register_cookies(cookies: list[dict]) -> None:
    """Register cookies for their domains in the global store."""
    for cookie in cookies:
        domain = cookie.get("domain", "")
        if domain:
            clean_domain = domain.lstrip(".")
            if clean_domain not in _cookie_store:
                _cookie_store[clean_domain] = []
            _cookie_store[clean_domain].append(cookie)


def get_cookies_for_url(url: str) -> list[dict] | None:
    """Get cookies that match the URL's domain."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if domain in _cookie_store:
        return _cookie_store[domain]

    for stored_domain, cookies in _cookie_store.items():
        if domain.endswith(stored_domain) or stored_domain.endswith(domain):
            return cookies

    return None
