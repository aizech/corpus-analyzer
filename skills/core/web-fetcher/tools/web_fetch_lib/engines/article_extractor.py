"""article-extractor engine for deterministic Markdown extraction."""

try:
    import article_extractor
except Exception:
    article_extractor = None  # type: ignore

from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.engines.static import _read_local_html
from web_fetch_lib.schemas import FetchResult


def _extract_links(html: str, base_url: str) -> list[str]:
    import re

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


class ArticleExtractorEngine(FetchEngine):
    """article-extractor: Readability-style extraction with HTTP/Playwright fetch."""

    name = "article_extractor"
    requires_browser = False

    def supports_url(self, url: str) -> bool:
        return not url.lower().endswith(".pdf")

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        if article_extractor is None:
            raise RuntimeError("article-extractor is not installed")

        if ctx.url.startswith(("http://", "https://")):
            result = await article_extractor.extract_article_from_url(
                ctx.url,
                prefer_playwright=ctx.render_js,
            )
        else:
            html, _ = _read_local_html(ctx.url)
            result = article_extractor.extract_article(html, url=ctx.url)

        if not result.success:
            raise RuntimeError(f"article-extractor failed: {result.error}")

        return FetchResult(
            url=ctx.url,
            title=result.title,
            markdown=result.markdown or "",
            links=_extract_links(getattr(result, "html", ""), ctx.url),
            images=[],
            metadata={"author": result.author, "date_published": result.date_published},
            render_path="browser" if ctx.render_js else "static",
            engine=self.name,
        )
