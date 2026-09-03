"""Headless Playwright extraction engine for JS-heavy or fallback pages."""

from urllib.parse import urlparse

from playwright.async_api import async_playwright
from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.schemas import FetchResult

_CONTENT_SELECTORS = [
    "main",
    "article",
    '[role="main"]',
    ".ms-rteElement",
    ".ms-rtestate-field",
    "div[data-sp-rte-databound]",
    "div.ms-rtestate-read",
]

_DEFAULT_TIMEOUT_SECONDS = 30.0


class PlaywrightRawEngine(FetchEngine):
    """Raw Playwright extraction engine for fallback browser rendering."""

    name = "playwright_raw"
    requires_browser = True

    def supports_url(self, url: str) -> bool:
        return url.startswith(("http://", "https://"))

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        timeout_seconds = ctx.timeout or _DEFAULT_TIMEOUT_SECONDS
        timeout_ms = int(timeout_seconds * 1000)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            pw_context = await browser.new_context()
            if ctx.cookies:
                await pw_context.add_cookies(ctx.cookies)
            page = await pw_context.new_page()

            try:
                await page.goto(ctx.url, wait_until=ctx.browser_wait_until, timeout=timeout_ms)
            except Exception:
                # If networkidle times out, fall back to the load event
                await page.goto(ctx.url, wait_until="load", timeout=timeout_ms)

            title = await page.title()

            markdown_parts: list[str] = [f"# {title}\n"]
            for selector in _CONTENT_SELECTORS:
                elements = await page.query_selector_all(selector)
                if elements:
                    for element in elements:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 50:
                            markdown_parts.append(text.strip())
                    break

            markdown = "\n\n".join(markdown_parts)
            if len(markdown) < 100:
                body = await page.query_selector("body")
                if body:
                    markdown = await body.inner_text()

            links: list[str] = []
            parsed = urlparse(ctx.url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            for link in await page.query_selector_all("a[href]"):
                href = await link.get_attribute("href")
                if href and href.startswith("http"):
                    links.append(href)
                elif href and href.startswith("/"):
                    links.append(base + href)

            images: list[str] = []
            for img in await page.query_selector_all("img[src]"):
                src = await img.get_attribute("src")
                if src and src.startswith("http"):
                    images.append(src)
                elif src and src.startswith("/"):
                    images.append(base + src)

            await browser.close()

        return FetchResult(
            url=ctx.url,
            title=title,
            markdown=markdown,
            links=list(dict.fromkeys(links)),
            images=list(dict.fromkeys(images)),
            metadata={"wait_until": ctx.browser_wait_until},
            render_path="browser",
            engine=self.name,
        )
