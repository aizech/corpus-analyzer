"""Auto engine that follows the default fallback routing."""

from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.engines.registry import fetch_with_fallback
from web_fetch_lib.schemas import FetchResult


class AutoEngine(FetchEngine):
    """Default routing engine: static engines first, then browser, then raw."""

    name = "auto"
    requires_browser = False

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        result = await fetch_with_fallback(ctx)
        actual_engine = result.engine
        result.engine = self.name
        result.metadata["actual_engine"] = actual_engine
        return result
