"""Vector store interface (Protocol).

The concrete Qdrant implementation is added in a later slice.
"""

from __future__ import annotations

from typing import Protocol

from app.models import Chunk


class SearchResult(Protocol):
    """A retrieved chunk with its similarity score."""

    chunk: Chunk
    score: float


class VectorStore(Protocol):
    """Stores chunk embeddings and supports similarity search."""

    async def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Insert or update chunk vectors and metadata."""
        ...

    async def search(self, vector: list[float], top_k: int) -> list[SearchResult]:
        """Return the ``top_k`` most similar chunks to ``vector``."""
        ...
