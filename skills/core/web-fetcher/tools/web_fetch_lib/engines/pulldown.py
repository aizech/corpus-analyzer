"""pulldown engine for HTTP-first Markdown extraction."""

try:
    import pulldown
except Exception:
    pulldown = None  # type: ignore

from typing import Any

from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.schemas import FetchResult


def _collect_links(result: Any) -> list[str]:
    return [link for link in getattr(result, "links", []) or [] if str(link).startswith("http")]


def _collect_images(result: Any) -> list[str]:
    return [img for img in getattr(result, "images", []) or [] if str(img).startswith("http")]


class PulldownEngine(FetchEngine):
    """HTTP-first Markdown extraction with optional Chromium rendering."""

    name = "pulldown"
    requires_browser = False

    def supports_url(self, url: str) -> bool:
        return url.startswith(("http://", "https://"))

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        if pulldown is None:
            raise RuntimeError("pulldown is not installed")

        result = await pulldown.fetch(
            ctx.url,
            detail=pulldown.Detail.readable,
            render=ctx.render_js,
            cookies=ctx.cookies,
            timeout=ctx.timeout or 30.0,
        )
        if not result.ok:
            raise RuntimeError(f"pulldown fetch failed: {result.error}")

        return FetchResult(
            url=ctx.url,
            title=result.title,
            markdown=result.content,
            links=_collect_links(result),
            images=_collect_images(result),
            metadata={
                "status_code": result.status_code,
                "routing": result.meta.get("routing") if result.meta else None,
            },
            render_path="browser" if ctx.render_js else "static",
            engine=self.name,
        )
