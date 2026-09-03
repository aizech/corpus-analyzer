"""Web fetch tool with pluggable engines, caching, and semantic chunking."""

import asyncio
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import nest_asyncio  # noqa: E402
from agno.tools import tool  # noqa: E402
from web_fetch_lib.cache import DiskCache  # noqa: E402
from web_fetch_lib.chunking import semantic_chunks  # noqa: E402
from web_fetch_lib.context import FetchContext  # noqa: E402
from web_fetch_lib.cookies import get_cookies_for_url, register_cookies  # noqa: E402
from web_fetch_lib.engines import fetch_with_fallback  # noqa: E402
from web_fetch_lib.schemas import FetchResult  # noqa: E402

nest_asyncio.apply()

__all__ = ["web_fetch", "register_cookies", "get_cookies_for_url", "_run_fetch"]

_DEFAULT_CACHE_DIR = Path("outputs") / "web_fetch_cache"
_DEFAULT_CACHE_TTL = 3600  # 1 hour
_BROWSER_CACHE_TTL = 600  # 10 minutes

_cache: DiskCache | None = None


def _get_cache() -> DiskCache:
    global _cache
    if _cache is None:
        _cache = DiskCache(_DEFAULT_CACHE_DIR, default_ttl=_DEFAULT_CACHE_TTL)
    return _cache


def _cache_key_args(
    url: str,
    render_js: bool,
    engine: str | None,
    timeout: float | None,
    browser_wait_until: str,
) -> dict:
    return {
        "url": url,
        "render_js": render_js,
        "engine": engine,
        "timeout": timeout,
        "browser_wait_until": browser_wait_until,
    }


def _chunk_result(result: FetchResult, max_tokens: int) -> FetchResult:
    result.chunks = semantic_chunks(result.markdown, max_tokens=max_tokens)
    return result


def _cap_result(result: FetchResult, max_total_tokens: int) -> FetchResult:
    """Limit the serialized result so it fits within the model context budget.

    Large pages (e.g. Amazon product pages with reviews and recommendations) can
    produce tens of thousands of tokens. This keeps the tool output bounded while
    preserving the most useful structured chunks and a preview of the full text.
    """
    if max_total_tokens <= 0:
        return result

    char_budget = max(1, max_total_tokens * 4)
    overhead = 1000
    refs_budget = 2000
    usable = max(1, char_budget - overhead - refs_budget)
    chunk_budget = int(usable * 0.6)
    markdown_budget = usable - chunk_budget

    def _fit_strings(items: list[str], budget: int) -> list[str]:
        kept: list[str] = []
        used = 0
        for item in items:
            if used + len(item) <= budget:
                kept.append(item)
                used += len(item)
            else:
                break
        return kept

    # Reference lists can explode on e-commerce sites; keep a useful subset.
    result.links = _fit_strings(result.links[:100], refs_budget // 2)
    result.images = _fit_strings(
        result.images[:100], refs_budget - sum(len(link) for link in result.links)
    )

    # Keep as many semantic chunks as fit into the chunk budget.
    kept_chunks = []
    used = 0
    for chunk in result.chunks:
        chunk_size = len(chunk.content) + len(str(chunk.heading)) + 50
        if used + chunk_size <= chunk_budget:
            kept_chunks.append(chunk)
            used += chunk_size
        else:
            break
    result.chunks = kept_chunks

    # Use the remaining budget for the full markdown preview.
    if len(result.markdown) > markdown_budget:
        trunc = result.markdown[:markdown_budget]
        for sep in ("\n\n", "\n", ". ", " "):
            idx = trunc.rfind(sep)
            if idx > markdown_budget * 0.7:
                trunc = trunc[:idx]
                break
        result.markdown = (
            trunc.strip()
            + "\n\n[Content truncated due to length; increase max_total_tokens for more.]"
        )

    return result


async def _run_fetch(
    url: str,
    render_js: bool = False,
    max_tokens: int = 6000,
    max_total_tokens: int = 8000,
    cookies: list[dict] | None = None,
    engine: str | None = None,
    use_cache: bool = True,
    timeout: float | None = None,
    browser_wait_until: str = "networkidle",
) -> dict:
    ctx = FetchContext(
        url=url,
        render_js=render_js,
        max_tokens=max_tokens,
        cookies=cookies,
        timeout=timeout,
        browser_wait_until=browser_wait_until,
        use_cache=use_cache,
    )

    cache = _get_cache()
    cache_key = _cache_key_args(url, render_js, engine, timeout, browser_wait_until)

    if use_cache:
        cached = cache.get(**cache_key)
        if cached is not None:
            return _cap_result(_chunk_result(cached, max_tokens), max_total_tokens).model_dump()

    result = await fetch_with_fallback(ctx, engine_name=engine)

    if use_cache:
        if result.render_path in {"browser", "manual"}:
            ttl = _BROWSER_CACHE_TTL
        else:
            ttl = _DEFAULT_CACHE_TTL
        cache.set(result, ttl=ttl, **cache_key)

    return _cap_result(_chunk_result(result, max_tokens), max_total_tokens).model_dump()


@tool
def web_fetch(
    url: str,
    render_js: bool = False,
    max_tokens: int = 6000,
    max_total_tokens: int = 8000,
    cookies: list[dict] | None = None,
    engine: str | None = None,
    use_cache: bool = True,
    timeout: float | None = None,
    browser_wait_until: str = "networkidle",
) -> dict:
    """
    Fetch a URL and return structured markdown content ready for downstream processing.

    Use this tool whenever you need to read content from a webpage, article, blog post,
    documentation URL, or local PDF file. Automatically falls back to browser rendering
    for JS-heavy pages (Next.js, Vue, Angular, Nuxt, React SPAs). Local PDFs are extracted
    with pypdf.

    Args:
        url: The full URL to fetch (http://, https://, file://, or a local path).
        render_js: Force Playwright/Crawl4AI browser rendering. Use True for SPAs,
                   Next.js, Vue, Angular, or login-gated pages.
        max_tokens: Approximate token budget per returned chunk (default 6000).
        max_total_tokens: Approximate token budget for the entire tool output
            (markdown + chunks + references). Default 8000 prevents context window
            overflows on large pages such as Amazon product pages.
        cookies: Optional list of cookie dicts for authentication (e.g., SharePoint).
                 Each cookie should have: name, value, domain, path.
        engine: Optional specific engine to use ("trafilatura", "trafilatura_tuned",
                "crawl4ai", "playwright_raw", "readability"). Defaults to auto fallback.
        use_cache: Whether to read/store results in the disk cache (default True).
        timeout: Request/page timeout in seconds (default 15 for static, 30 for browser).
        browser_wait_until: Playwright wait_until value (default "networkidle").

    Returns:
        A dict with: url, title, markdown, links, images, metadata, chunks, render_path,
        engine, cached.
        - markdown: extracted article text as markdown (may be truncated to fit
            max_total_tokens)
        - chunks: list of {heading, content, tokens_estimate} sections, each <= max_tokens
        - render_path: "static", "browser", or "pdf" — which path was used
        - engine: name of the engine that produced the result
    """
    return asyncio.run(
        _run_fetch(
            url=url,
            render_js=render_js,
            max_tokens=max_tokens,
            max_total_tokens=max_total_tokens,
            cookies=cookies,
            engine=engine,
            use_cache=use_cache,
            timeout=timeout,
            browser_wait_until=browser_wait_until,
        )
    )
