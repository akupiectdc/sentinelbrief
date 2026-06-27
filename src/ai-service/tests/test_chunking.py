"""Chunking tests."""

from __future__ import annotations

import pytest

from app.documents.chunking import chunk_text


def _chunk(text: str, size: int = 100, overlap: int = 20):
    return chunk_text(
        text,
        document_id="doc-1",
        source_title="Title",
        source_type="synthetic",
        chunk_size=size,
        chunk_overlap=overlap,
    )


def test_chunking_produces_expected_windows() -> None:
    chunks = _chunk("x" * 250, size=100, overlap=20)
    # step = 80 -> windows starting at 0, 80, 160
    assert len(chunks) == 3
    assert chunks[0].character_start == 0
    assert chunks[0].character_end == 100
    assert chunks[1].character_start == 80
    assert chunks[2].character_end == 250


def test_chunking_overlap_is_applied() -> None:
    text = "".join(str(i % 10) for i in range(250))
    chunks = _chunk(text, size=100, overlap=20)
    # The overlap region of consecutive chunks must match.
    assert chunks[0].text[-20:] == chunks[1].text[:20]


def test_chunk_ids_are_unique_and_carry_metadata() -> None:
    chunks = _chunk("y" * 300)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))
    assert all(c.source_title == "Title" for c in chunks)
    assert all(c.source_type == "synthetic" for c in chunks)


def test_empty_text_yields_no_chunks() -> None:
    assert _chunk("   ") == []


def test_overlap_must_be_smaller_than_size() -> None:
    with pytest.raises(ValueError):
        _chunk("hello", size=50, overlap=50)
