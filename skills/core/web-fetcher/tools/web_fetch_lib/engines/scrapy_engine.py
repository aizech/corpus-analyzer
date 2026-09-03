"""Scrapy-based engine using Selector + html-to-markdown."""

import httpx

try:
    from scrapy.http import HtmlResponse
except Exception:
    HtmlResponse = None  # type: ignore

from typing import Any

from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.engines.static import _read_local_html
from web_fetch_lib.schemas import FetchResult

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


def _extract_text(response: Any) -> str:
    """Select the best candidate HTML and convert to Markdown."""
    for xpath in ["//main", "//article", "//body"]:
        nodes = response.xpath(xpath)
        if nodes:
            return _html_to_markdown(nodes[0].get())
    return ""


class ScrapyEngine(FetchEngine):
    """Scrapy HTTP fetch + Selector + html-to-markdown extraction."""

    name = "scrapy"
    requires_browser = False

    def supports_url(self, url: str) -> bool:
        return not url.lower().endswith(".pdf")

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        if HtmlResponse is None:
            raise RuntimeError("scrapy is not installed")

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

        scrapy_response = HtmlResponse(url=ctx.url, body=html.encode("utf-8"), encoding="utf-8")

        title = (
            scrapy_response.xpath("//title/text()").get("").strip()
            or scrapy_response.xpath("//h1/text()").get("").strip()
        )
        markdown = _extract_text(scrapy_response)

        links = [
            href.strip()
            for href in scrapy_response.xpath("//a/@href").getall()
            if href and href.startswith("http")
        ]
        images = [
            src.strip()
            for src in scrapy_response.xpath("//img/@src").getall()
            if src and src.startswith("http")
        ]

        return FetchResult(
            url=ctx.url,
            title=title,
            markdown=markdown,
            links=list(dict.fromkeys(links)),
            images=list(dict.fromkeys(images)),
            metadata={"status_code": status_code},
            render_path="static",
            engine=self.name,
        )
