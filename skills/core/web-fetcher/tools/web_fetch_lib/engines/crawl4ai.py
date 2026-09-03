"""Browser-based fetch engine backed by Crawl4AI."""

from crawl4ai import AsyncWebCrawler

try:
    from crawl4ai import BrowserConfig, CrawlerRunConfig
except Exception:
    BrowserConfig = None
    CrawlerRunConfig = None

from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.schemas import FetchResult


def _collect_links(raw_links: object) -> list[str]:
    if isinstance(raw_links, dict):
        hrefs: list[str] = []
        for group in raw_links.values():
            if isinstance(group, list):
                for item in group:
                    href = item.get("href") if isinstance(item, dict) else str(item)
                    if href and str(href).startswith("http"):
                        hrefs.append(str(href))
        return list(dict.fromkeys(hrefs))
    if isinstance(raw_links, list):
        return [str(x) for x in raw_links if str(x).startswith("http")]
    return []


def _collect_images(raw_media: object) -> list[str]:
    if isinstance(raw_media, dict):
        srcs: list[str] = []
        for item in raw_media.get("images", []):
            src = item.get("src") if isinstance(item, dict) else str(item)
            if src and str(src).startswith("http"):
                srcs.append(str(src))
        return list(dict.fromkeys(srcs))
    return []


class Crawl4AiEngine(FetchEngine):
    """Browser rendering engine using Crawl4AI's AsyncWebCrawler."""

    name = "crawl4ai"
    requires_browser = True

    def supports_url(self, url: str) -> bool:
        return url.startswith(("http://", "https://"))

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        crawler_kwargs: dict = {}
        arun_kwargs: dict = {}

        if CrawlerRunConfig is not None and BrowserConfig is not None:
            crawler_kwargs["config"] = BrowserConfig(
                headless=True,
                cookies=ctx.cookies or [],
                verbose=False,
            )
            page_timeout_ms = int((ctx.timeout or 30.0) * 1000)
            arun_kwargs["config"] = CrawlerRunConfig(
                page_timeout=page_timeout_ms,
                wait_until=ctx.browser_wait_until,
            )
        else:
            crawler_kwargs["headless"] = True
            if ctx.cookies:
                crawler_kwargs["cookies"] = ctx.cookies

        async with AsyncWebCrawler(**crawler_kwargs) as crawler:
            result = await crawler.arun(url=ctx.url, **arun_kwargs)

        markdown: str = result.markdown or ""
        metadata: dict = result.metadata or {}
        title: str | None = metadata.get("title") or None

        return FetchResult(
            url=ctx.url,
            title=title,
            markdown=markdown,
            links=_collect_links(result.links),
            images=_collect_images(result.media),
            metadata=metadata,
            render_path="browser",
            engine=self.name,
        )
