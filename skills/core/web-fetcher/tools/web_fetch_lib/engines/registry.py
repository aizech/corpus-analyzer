"""Registry of fetch engines and fallback routing."""

import logging

from web_fetch_lib.context import FetchContext
from web_fetch_lib.cookies import get_cookies_for_url
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.quality import is_low_quality
from web_fetch_lib.schemas import FetchResult

logger = logging.getLogger(__name__)


def _load_engines() -> dict[str, FetchEngine]:
    """Load engines lazily so missing optional dependencies don't break the whole tool."""
    engines: dict[str, FetchEngine] = {}
    engine_imports = [
        ("trafilatura", "web_fetch_lib.engines.static", "TrafilaturaEngine"),
        ("trafilatura_tuned", "web_fetch_lib.engines.static", "TrafilaturaTunedEngine"),
        ("crawl4ai", "web_fetch_lib.engines.crawl4ai", "Crawl4AiEngine"),
        ("playwright_raw", "web_fetch_lib.engines.playwright_raw", "PlaywrightRawEngine"),
        ("readability", "web_fetch_lib.engines.readability", "ReadabilityEngine"),
        ("readability_lxml", "web_fetch_lib.engines.readability_lxml", "ReadabilityLxmlEngine"),
        ("pulldown", "web_fetch_lib.engines.pulldown", "PulldownEngine"),
        ("article_extractor", "web_fetch_lib.engines.article_extractor", "ArticleExtractorEngine"),
        ("scrapy", "web_fetch_lib.engines.scrapy_engine", "ScrapyEngine"),
        ("pdf", "web_fetch_lib.engines.pdf", "PdfEngine"),
    ]
    for name, module, cls in engine_imports:
        try:
            mod = __import__(module, fromlist=[cls])
            engines[name] = getattr(mod, cls)()
        except Exception as exc:
            logger.debug("Engine %s not available: %s", name, exc)
    return engines


ENGINES: dict[str, FetchEngine] = _load_engines()

_STATIC_ENGINES: list[str] = [
    "trafilatura",
    "trafilatura_tuned",
    "readability",
    "readability_lxml",
    "article_extractor",
    "scrapy",
]
_BROWSER_ENGINES: list[str] = ["crawl4ai", "playwright_raw", "pulldown"]


def get_engine(name: str) -> FetchEngine:
    if name not in ENGINES:
        raise ValueError(f"Unknown engine '{name}'. Available: {list(ENGINES)}")
    return ENGINES[name]


async def fetch_with_engine(ctx: FetchContext, engine_name: str) -> FetchResult:
    """Fetch a URL with a specific engine."""
    engine = get_engine(engine_name)
    return await engine.fetch(ctx)


async def fetch_with_fallback(ctx: FetchContext, engine_name: str | None = None) -> FetchResult:
    """Fetch a URL using the best available engine, falling back on low quality.

    Order:
      1. PDF files always route to the PDF engine.
      2. If an explicit engine_name is given, use that engine only.
      3. If render_js is True, prefer browser engines.
      4. Otherwise try static engines first, then browser engines.
    """
    from web_fetch_lib.engines.pdf import is_pdf_url

    if is_pdf_url(ctx.url):
        return await ENGINES["pdf"].fetch(ctx)

    # Auto-detect cookies from the global store if none were supplied
    if not ctx.cookies:
        ctx.cookies = get_cookies_for_url(ctx.url)

    if engine_name:
        return await ENGINES[engine_name].fetch(ctx)

    engine_order = list(_BROWSER_ENGINES) if ctx.render_js else list(_STATIC_ENGINES)
    if not ctx.render_js:
        engine_order.extend(_BROWSER_ENGINES)

    last_error: Exception | None = None
    chosen_name: str | None = None
    result: FetchResult | None = None
    for name in engine_order:
        engine = ENGINES.get(name)
        if engine is None or not engine.supports_url(ctx.url):
            continue
        try:
            result = await engine.fetch(ctx)
            chosen_name = name
            if not is_low_quality(result):
                result.engine = name
                return result
            # low quality: keep result and try next engine
        except Exception as exc:
            last_error = exc
            continue

    # If nothing succeeded, return the last result we got or re-raise the last error.
    if result is not None:
        result.engine = chosen_name or engine_order[-1]
        return result
    if last_error:
        raise last_error
    raise RuntimeError("No fetch engine could process the URL")
