"""In-memory document store tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.documents.store import InMemoryDocumentStore
from app.models import Chunk, DocumentMetadata


def _metadata(document_id: str) -> DocumentMetadata:
    return DocumentMetadata(
        document_id=document_id,
        title="Title",
        source_type="synthetic",
        language="en",
        ingested_at=datetime.now(UTC),
        chunk_count=1,
    )


def _chunk(document_id: str) -> Chunk:
    return Chunk(
        document_id=document_id,
        chunk_id=f"{document_id}::chunk-0",
        source_title="Title",
        source_type="synthetic",
        text="hello",
        character_start=0,
        character_end=5,
    )


def test_add_and_get() -> None:
    store = InMemoryDocumentStore()
    store.add(_metadata("a"), [_chunk("a")])
    stored = store.get("a")
    assert stored is not None
    assert stored.metadata.document_id == "a"
    assert len(stored.chunks) == 1


def test_get_unknown_returns_none() -> None:
    store = InMemoryDocumentStore()
    assert store.get("missing") is None


def test_list_and_clear() -> None:
    store = InMemoryDocumentStore()
    store.add(_metadata("a"), [_chunk("a")])
    store.add(_metadata("b"), [_chunk("b")])
    assert len(store.list()) == 2
    store.clear()
    assert store.list() == []
