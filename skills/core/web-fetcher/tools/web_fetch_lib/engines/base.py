"""Base protocol for web_fetch extraction engines."""

from abc import ABC, abstractmethod

from web_fetch_lib.context import FetchContext
from web_fetch_lib.schemas import FetchResult


class FetchEngine(ABC):
    """Abstract base class for an engine that fetches a URL and returns a FetchResult."""

    name: str = "abstract"
    requires_browser: bool = False

    def supports_url(self, url: str) -> bool:
        """Return True if this engine can handle the given URL."""
        return True

    @abstractmethod
    async def fetch(self, ctx: FetchContext) -> FetchResult:
        """Fetch and extract content for the URL described by *ctx*."""
        ...
