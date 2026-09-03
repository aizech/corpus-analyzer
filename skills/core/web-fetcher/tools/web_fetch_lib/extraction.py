import re
from typing import Optional

import httpx
import trafilatura
from bs4 import BeautifulSoup
from web_fetch_lib.schemas import FetchResult

_JS_TRIGGERS = [
    "__NEXT_DATA__",
    "__nuxt",
    "ng-version",
    "ember-application",
    "react-app",
    "webpack",
    "hydration",
    "application/json",
    "data-reactroot",
    "vue-app",
]

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def requires_browser(html: str) -> bool:
    return any(trigger in html for trigger in _JS_TRIGGERS)


def _extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if href.startswith("http"):
            links.append(href)
        elif href.startswith("/"):
            match = re.match(r"(https?://[^/]+)", base_url)
            if match:
                links.append(match.group(1) + href)
    return list(dict.fromkeys(links))


def _extract_images(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for tag in soup.find_all("img", src=True):
        src = tag["src"].strip()
        if src.startswith("http"):
            images.append(src)
        elif src.startswith("/"):
            match = re.match(r"(https?://[^/]+)", base_url)
            if match:
                images.append(match.group(1) + src)
    return list(dict.fromkeys(images))


def _extract_title(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()
    return None


async def fetch_static(url: str) -> tuple[FetchResult, bool]:
    """
    Fetch a URL with httpx.AsyncClient.

    Returns (FetchResult, needs_browser) where needs_browser=True signals
    the caller should fall back to the browser engine.
    """
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=15.0,
        headers=_DEFAULT_HEADERS,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        html = response.text

    if requires_browser(html):
        return FetchResult(url=url, markdown=""), True

    markdown = (
        trafilatura.extract(
            html,
            output_format="markdown",
            include_links=True,
            include_images=True,
            no_fallback=False,
        )
        or ""
    )

    title = _extract_title(html)
    links = _extract_links(html, url)
    images = _extract_images(html, url)

    return (
        FetchResult(
            url=url,
            title=title,
            markdown=markdown,
            links=links,
            images=images,
            metadata={"status_code": response.status_code},
            render_path="static",
        ),
        False,
    )
