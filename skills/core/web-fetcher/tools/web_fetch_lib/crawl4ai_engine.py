from typing import Optional

from crawl4ai import AsyncWebCrawler
from web_fetch_lib.schemas import FetchResult


def _collect_links(raw_links: object) -> list[str]:
    """Normalise the links field which Crawl4AI returns as dict or list."""
    if isinstance(raw_links, dict):
        hrefs = []
        for group in raw_links.values():
            if isinstance(group, list):
                for item in group:
                    href = item.get("href") if isinstance(item, dict) else str(item)
                    if href and href.startswith("http"):
                        hrefs.append(href)
        return list(dict.fromkeys(hrefs))
    if isinstance(raw_links, list):
        return [str(x) for x in raw_links if str(x).startswith("http")]
    return []


def _collect_images(raw_media: object) -> list[str]:
    """Normalise the media field which Crawl4AI returns as dict or list."""
    if isinstance(raw_media, dict):
        srcs = []
        for item in raw_media.get("images", []):
            src = item.get("src") if isinstance(item, dict) else str(item)
            if src and src.startswith("http"):
                srcs.append(src)
        return list(dict.fromkeys(srcs))
    return []


async def fetch_browser(url: str, cookies: Optional[list[dict]] = None) -> FetchResult:
    """
    Fetch a URL using Crawl4AI's AsyncWebCrawler (Playwright-backed).
    Used as fallback for JS-rendered or dynamic pages.

    Args:
        url: The URL to fetch
        cookies: Optional list of cookie dicts for authentication (e.g., SharePoint)
                 Each cookie should have: name, value, domain, path
    """
    crawler_config = {"headless": True}
    if cookies:
        crawler_config["cookies"] = cookies

    async with AsyncWebCrawler(**crawler_config) as crawler:
        result = await crawler.arun(url=url)

    markdown: str = result.markdown or ""
    metadata: dict = result.metadata or {}
    title: str | None = metadata.get("title") or None

    links = _collect_links(result.links)
    images = _collect_images(result.media)

    return FetchResult(
        url=url,
        title=title,
        markdown=markdown,
        links=links,
        images=images,
        metadata=metadata,
        render_path="browser",
    )
