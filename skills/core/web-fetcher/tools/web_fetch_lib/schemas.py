from pydantic import BaseModel


class Chunk(BaseModel):
    heading: str | None
    content: str
    tokens_estimate: int


class FetchResult(BaseModel):
    url: str
    title: str | None = None
    markdown: str
    summary: str | None = None
    links: list[str] = []
    images: list[str] = []
    metadata: dict = {}
    chunks: list[Chunk] = []
    render_path: str = "static"
    engine: str | None = None
    cached: bool = False
