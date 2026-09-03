"""Pluggable fetch engines for web_fetch."""

from web_fetch_lib.engines.auto import AutoEngine
from web_fetch_lib.engines.registry import (
    ENGINES,
    fetch_with_engine,
    fetch_with_fallback,
    get_engine,
)

# Register the default auto-routing engine for benchmarking and explicit use.
ENGINES["auto"] = AutoEngine()

__all__ = ["ENGINES", "fetch_with_engine", "fetch_with_fallback", "get_engine"]
