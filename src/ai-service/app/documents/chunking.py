"""Deterministic, character-based chunking with overlap."""

from __future__ import annotations

from app.models import Chunk


def chunk_text(
    text: str,
    *,
    document_id: str,
    source_title: str,
    source_type: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    """Split ``text`` into overlapping character windows.

    Each chunk records its source metadata and character offsets so it can be
    embedded and cited later.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()
    chunks: list[Chunk] = []
    if not text:
        return chunks

    step = chunk_size - chunk_overlap
    index = 0
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(
            Chunk(
                document_id=document_id,
                chunk_id=f"{document_id}::chunk-{index}",
                source_title=source_title,
                source_type=source_type,
                text=text[start:end],
                character_start=start,
                character_end=end,
            )
        )
        index += 1
        if end >= length:
            break
        start += step

    return chunks
