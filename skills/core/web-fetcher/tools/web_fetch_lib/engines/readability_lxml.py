"""readability-lxml engine for article extraction."""

import re

import httpx
from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.engines.static import _read_local_html
from web_fetch_lib.schemas import FetchResult

try:
    from readability.readability import Document
except Exception:
    Document = None  # type: ignore

try:
    import html_to_markdown
except Exception:
    html_to_markdown = None

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _html_to_markdown(html: str) -> str:
    if html_to_markdown is None:
        raise RuntimeError("html-to-markdown is not installed")
    return html_to_markdown.convert(html).content


def _extract_title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r"\s+", " ", match.group(1)).strip()
    return ""


def _extract_links(html: str, base_url: str) -> list[str]:
    links: list[str] = []
    domain_match = re.match(r"(https?://[^/]+)", base_url)
    domain = domain_match.group(1) if domain_match else ""
    for m in re.finditer(r'href=["\'](.*?)["\']', html, re.IGNORECASE):
        href = m.group(1).strip()
        if href.startswith("http"):
            links.append(href)
        elif domain and href.startswith("/"):
            links.append(domain + href)
    return list(dict.fromkeys(links))


class ReadabilityLxmlEngine(FetchEngine):
    """readability-lxml + html-to-markdown extraction engine."""

    name = "readability_lxml"
    requires_browser = False

    def supports_url(self, url: str) -> bool:
        return not url.lower().endswith(".pdf")

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        if Document is None:
            raise RuntimeError("readability-lxml is not installed")

        if ctx.url.startswith(("http://", "https://")):
            timeout = ctx.timeout or 15.0
            async with httpx.AsyncClient(
                follow_redirects=True, timeout=timeout, headers=_DEFAULT_HEADERS
            ) as client:
                response = await client.get(ctx.url)
                response.raise_for_status()
                html = response.text
                status_code = response.status_code
        else:
            html, status_code = _read_local_html(ctx.url)

        doc = Document(html)
        title = doc.short_title() or _extract_title(html)
        summary_html = doc.summary()
        markdown = _html_to_markdown(summary_html)

        return FetchResult(
            url=ctx.url,
            title=title,
            markdown=markdown,
            links=_extract_links(html, ctx.url),
            images=[],
            metadata={"status_code": status_code},
            render_path="static",
            engine=self.name,
        )
