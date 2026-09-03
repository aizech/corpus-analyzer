"""Benchmark metrics for fetch results."""

from web_fetch_lib.quality import boilerplate_score, heading_count
from web_fetch_lib.schemas import FetchResult


def compute_metrics(result: FetchResult, elapsed_ms: float) -> dict:
    text = (result.markdown or "").strip()
    title = (result.title or "").strip()
    return {
        "success": True,
        "elapsed_ms": round(elapsed_ms, 2),
        "chars": len(text),
        "headings": heading_count(text),
        "links": len(result.links or []),
        "images": len(result.images or []),
        "title_present": bool(title),
        "boilerplate_score": round(boilerplate_score(text), 4),
        "render_path": result.render_path,
        "engine": result.engine,
        "cached": result.cached,
    }


def compute_error_metrics(error: Exception, elapsed_ms: float) -> dict:
    return {
        "success": False,
        "elapsed_ms": round(elapsed_ms, 2),
        "error": f"{type(error).__name__}: {error}",
    }
