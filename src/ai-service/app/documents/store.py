"""In-memory document store.

A simple repository used in early slices. It will be superseded by Qdrant-backed
persistence for vectors in a later slice; this store keeps the document metadata
and chunk text for ingestion and debugging.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from app.models import Chunk, DocumentMetadata


@dataclass
class StoredDocument:
    """A document's metadata together with its chunks."""

    metadata: DocumentMetadata
    chunks: list[Chunk]


class InMemoryDocumentStore:
    """Process-local document store. Not persistent; intended for demos/tests."""

    def __init__(self) -> None:
        self._documents: dict[str, StoredDocument] = {}

    def add(self, metadata: DocumentMetadata, chunks: list[Chunk]) -> StoredDocument:
        stored = StoredDocument(metadata=metadata, chunks=chunks)
        self._documents[metadata.document_id] = stored
        return stored

    def get(self, document_id: str) -> StoredDocument | None:
        return self._documents.get(document_id)

    def list(self) -> list[StoredDocument]:
        return list(self._documents.values())

    def clear(self) -> None:
        self._documents.clear()


@lru_cache
def get_document_store() -> InMemoryDocumentStore:
    """Return the cached process-wide document store."""
    return InMemoryDocumentStore()
