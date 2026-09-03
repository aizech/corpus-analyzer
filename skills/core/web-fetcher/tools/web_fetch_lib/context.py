"""Execution context passed to every fetch engine."""

from dataclasses import dataclass, field


@dataclass
class FetchContext:
    """Inputs and options for a single fetch operation."""

    url: str
    render_js: bool = False
    max_tokens: int = 6000
    cookies: list[dict] | None = None
    timeout: float | None = None
    browser_wait_until: str = "networkidle"
    headers: dict | None = None
    use_cache: bool = True
    extra: dict = field(default_factory=dict)
