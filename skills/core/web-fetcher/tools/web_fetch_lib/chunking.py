import re

from web_fetch_lib.schemas import Chunk

_HEADING_RE = re.compile(r"(?m)^(#{1,3} .+)$")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _char_budget(max_tokens: int) -> int:
    return max(1, max_tokens * 4)


def _split_oversized(text: str, max_tokens: int) -> list[str]:
    """Split *text* into pieces that each fit within *max_tokens*.

    First tries sentence boundaries, then paragraph-style blank lines,
    then simple character chunks.
    """
    budget = _char_budget(max_tokens)
    if len(text) <= budget:
        return [text]

    pieces: list[str] = []
    for sentence in _SENTENCE_RE.split(text):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) <= budget:
            pieces.append(sentence)
            continue
        # Very long sentence / list: split into fixed-size chunks.
        for i in range(0, len(sentence), budget):
            piece = sentence[i : i + budget].strip()
            if piece:
                pieces.append(piece)
    return pieces or [text[:budget]]


def _chunk_section(heading: str | None, text: str, max_tokens: int) -> list[Chunk]:
    """Split one section into one or more chunks that each fit within max_tokens."""
    budget = _char_budget(max_tokens)
    prefix = f"{heading}\n\n" if heading else ""

    if len(prefix + text) <= budget:
        full = f"{prefix}{text}".strip()
        return [Chunk(heading=heading, content=full, tokens_estimate=_estimate_tokens(full))]

    chunks: list[Chunk] = []
    # Try paragraph boundaries first.
    paragraphs = re.split(r"\n{2,}", text)
    current = prefix

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= budget:
            current = candidate
            continue
        if current:
            chunks.append(
                Chunk(
                    heading=heading,
                    content=current,
                    tokens_estimate=_estimate_tokens(current),
                )
            )
            current = ""
        if len(para) <= budget:
            current = para
        else:
            for piece in _split_oversized(para, max_tokens):
                chunks.append(
                    Chunk(
                        heading=heading,
                        content=piece,
                        tokens_estimate=_estimate_tokens(piece),
                    )
                )

    if current:
        chunks.append(
            Chunk(heading=heading, content=current, tokens_estimate=_estimate_tokens(current))
        )

    return chunks


def semantic_chunks(markdown: str, max_tokens: int = 4000) -> list[Chunk]:
    """
    Split markdown into semantic chunks on H1/H2/H3 boundaries.

    Each returned chunk fits within *max_tokens* and the union of all chunks
    contains the full input text (no silent truncation).
    """
    if not markdown:
        return []

    if max_tokens <= 0:
        return [
            Chunk(
                heading=None,
                content=markdown.strip(),
                tokens_estimate=_estimate_tokens(markdown.strip()),
            )
        ]

    parts: list[tuple[str | None, str]] = []
    current_heading: str | None = None
    current_start = 0

    for match in _HEADING_RE.finditer(markdown):
        pre = markdown[current_start : match.start()].strip()
        if pre or current_heading:
            parts.append((current_heading, pre))
        current_heading = match.group(1).strip()
        current_start = match.end()

    tail = markdown[current_start:].strip()
    if tail or current_heading:
        parts.append((current_heading, tail))

    chunks: list[Chunk] = []
    for heading, content in parts:
        if not content.strip() and not heading:
            continue
        chunks.extend(_chunk_section(heading, content, max_tokens))

    return chunks
