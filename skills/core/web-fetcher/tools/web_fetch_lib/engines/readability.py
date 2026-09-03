"""Pure-Python article extraction fallback using zerodep.readability."""

import re

import httpx
from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.schemas import FetchResult

try:
    from zerodep.readability import extract as readability_extract
except Exception:
    readability_extract = None

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _title_from_html(html: str) -> str:
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


class ReadabilityEngine(FetchEngine):
    """Lightweight article extraction with zerodep.readability (stdlib only)."""

    name = "readability"
    requires_browser = False

    def supports_url(self, url: str) -> bool:
        return not url.lower().endswith(".pdf")

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        if readability_extract is None:
            raise RuntimeError("zerodep is not installed; install with pip install zerodep")

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=ctx.timeout or 15.0,
            headers=_DEFAULT_HEADERS,
        ) as client:
            response = await client.get(ctx.url)
            response.raise_for_status()
            html = response.text

        article = readability_extract(html, url=ctx.url)
        if isinstance(article, dict):
            markdown = article.get("text", "").strip()
        else:
            markdown = str(article).strip()

        return FetchResult(
            url=ctx.url,
            title=article.get("title") if isinstance(article, dict) else _title_from_html(html),
            markdown=markdown,
            links=_extract_links(html, ctx.url),
            images=[],
            metadata={"status_code": response.status_code},
            render_path="static",
            engine=self.name,
        )
