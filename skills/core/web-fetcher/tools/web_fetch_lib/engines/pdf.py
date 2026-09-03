"""PDF extraction engine for local file:// or plain filesystem paths."""

from pathlib import Path

from web_fetch_lib.context import FetchContext
from web_fetch_lib.engines.base import FetchEngine
from web_fetch_lib.schemas import FetchResult

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


def _resolve_local_path(url: str) -> Path | None:
    """Return a Path for a file:// URL or a plain local path, otherwise None."""
    if url.startswith("file://"):
        raw_path = url[7:]
        # Windows file:// URLs often have a leading slash before the drive letter.
        if raw_path.startswith("/") and len(raw_path) > 2 and raw_path[2] == ":":
            raw_path = raw_path[1:]
        return Path(raw_path)
    if url.startswith("http://") or url.startswith("https://"):
        return None
    return Path(url)


def _extract_pdf_text(path: Path) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf is not installed; cannot extract PDF text.")
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text.strip())
    return "\n\n".join(parts)


class PdfEngine(FetchEngine):
    """Extract text from a local PDF file."""

    name = "pdf"
    requires_browser = False

    def supports_url(self, url: str) -> bool:
        return is_pdf_url(url)

    async def fetch(self, ctx: FetchContext) -> FetchResult:
        path = _resolve_local_path(ctx.url)
        if path is None:
            raise ValueError(f"PDF engine only supports local paths or file:// URLs: {ctx.url}")
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")
        text = _extract_pdf_text(path)
        return FetchResult(
            url=ctx.url,
            title=path.stem,
            markdown=text,
            links=[],
            images=[],
            metadata={"source": "local_pdf", "path": str(path)},
            render_path="pdf",
            engine=self.name,
        )


def is_pdf_url(url: str) -> bool:
    path = _resolve_local_path(url)
    return path is not None and path.suffix.lower() == ".pdf"
