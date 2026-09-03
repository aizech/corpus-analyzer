"""Static HTTP fetch engine backed by httpx and trafilatura."""

import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
import trafilatura
from bs4 import BeautifulSoup
from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
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


def _requires_browser(html: str) -> bool:
    return any(trigger in html for trigger in _JS_TRIGGERS)


def _extract_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()
    return None


def _is_local_path(url: str) -> bool:
    return url.startswith("file://") or not url.startswith(("http://", "https://"))


def _read_local_html(url: str) -> tuple[str, int]:
    """Read a local HTML file and return (html, status_code)."""
    if url.startswith("file://"):
        raw_path = url[7:]
        # Windows file:// URLs often have a leading slash before the drive letter.
        if raw_path.startswith("/") and len(raw_path) > 2 and raw_path[2] == ":":
            raw_path = raw_path[1:]
        path = Path(raw_path)
    else:
        path = Path(url)
    if not path.exists():
        raise FileNotFoundError(f"HTML fixture not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"{path} is a directory; use the local_summarize tool for folders")
    return path.read_text(encoding="utf-8"), 200


def _extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    domain_match = re.match(r"(https?://[^/]+)", base_url)
    domain = domain_match.group(1) if domain_match else ""
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if href.startswith("http"):
            links.append(href)
        elif domain and href.startswith("/"):
            links.append(domain + href)
    return list(dict.fromkeys(links))


def _extract_images(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    images: list[str] = []
    domain_match = re.match(r"(https?://[^/]+)", base_url)
    domain = domain_match.group(1) if domain_match else ""
    for tag in soup.find_all("img", src=True):
        src = tag["src"].strip()
        if src.startswith("http"):
            images.append(src)
        elif domain and src.startswith("/"):
            images.append(domain + src)
    return list(dict.fromkeys(images))


def _is_pdf_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.path.lower().endswith(".pdf")


class TrafilaturaEngine(FetchEngine):
    """Fast static fetch engine using httpx + trafilatura."""

    name = "trafilatura"
    requires_browser = False

    def supports_url(self, url: str) -> bool:
        return not _is_pdf_url(url)

    def __init__(
        self,
        favor_precision: bool = False,
        favor_recall: bool = False,
        fast: bool = False,
        include_formatting: bool = False,
    ) -> None:
        self.favor_precision = favor_precision
        self.favor_recall = favor_recall
        self.fast = fast
        self.include_formatting = include_formatting

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        headers = {**_DEFAULT_HEADERS, **(ctx.headers or {})}

        if _is_local_path(ctx.url):
            html, status_code = _read_local_html(ctx.url)
        else:
            timeout = ctx.timeout or 15.0
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=timeout,
                headers=headers,
            ) as client:
                response = await client.get(ctx.url)
                response.raise_for_status()
                html = response.text
                status_code = response.status_code

        if _requires_browser(html):
            return FetchResult(
                url=ctx.url,
                markdown="",
                metadata={"requires_browser": True, "status_code": status_code},
                render_path="static",
                engine=self.name,
            )

        extract_kwargs: dict = {
            "output_format": "markdown",
            "include_links": True,
            "include_images": True,
            "no_fallback": False,
        }
        if self.favor_precision:
            extract_kwargs["favor_precision"] = True
        if self.favor_recall:
            extract_kwargs["favor_recall"] = True
        if self.fast:
            extract_kwargs["fast"] = True
        if self.include_formatting:
            extract_kwargs["include_formatting"] = True

        markdown = trafilatura.extract(html, **extract_kwargs) or ""

        return FetchResult(
            url=ctx.url,
            title=_extract_title(html),
            markdown=markdown,
            links=_extract_links(html, ctx.url),
            images=_extract_images(html, ctx.url),
            metadata={"status_code": status_code},
            render_path="static",
            engine=self.name,
        )


class TrafilaturaTunedEngine(TrafilaturaEngine):
    """Static variant tuned for article recall and metadata."""

    name = "trafilatura_tuned"

    def __init__(self) -> None:
        super().__init__(favor_recall=True, include_formatting=True)
