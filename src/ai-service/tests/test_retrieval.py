"""Retrieval tests using a fake embedder and in-memory Qdrant."""

from __future__ import annotations

import asyncio

from qdrant_client import AsyncQdrantClient

from app.models import Chunk
from app.rag.retrieval import retrieve
from app.vectorstores.qdrant import QdrantVectorStore


class _FixedEmbedder:
    """Maps known texts to fixed vectors; unknown texts to a neutral vector."""

    def __init__(self, mapping: dict[str, list[float]]) -> None:
        self._mapping = mapping

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._mapping.get(text, [0.0, 0.0, 1.0]) for text in texts]


def _chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(
        document_id="doc-1",
        chunk_id=chunk_id,
        source_title="Title",
        source_type="synthetic",
        text=text,
        character_start=0,
        character_end=len(text),
    )


async def _seeded_store() -> QdrantVectorStore:
    client = AsyncQdrantClient(location=":memory:")
    store = QdrantVectorStore("retrieval_test", client=client)
    await store.upsert(
        [_chunk("doc-1::chunk-0", "alpha"), _chunk("doc-1::chunk-1", "beta")],
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
    )
    return store


def test_retrieve_returns_nearest_first() -> None:
    async def run():
        store = await _seeded_store()
        embedder = _FixedEmbedder({"find alpha": [0.95, 0.05, 0.0]})
        return await retrieve(
            "find alpha", embedder=embedder, vector_store=store, top_k=2, min_score=0.0
        )

    results = asyncio.run(run())
    assert results[0].chunk.chunk_id == "doc-1::chunk-0"


def test_retrieve_filters_by_min_score() -> None:
    async def run():
        store = await _seeded_store()
        # Query close to chunk-0, nearly orthogonal to chunk-1.
        embedder = _FixedEmbedder({"q": [1.0, 0.0, 0.0]})
        return await retrieve(
            "q", embedder=embedder, vector_store=store, top_k=5, min_score=0.5
        )

    results = asyncio.run(run())
    assert len(results) == 1
    assert results[0].chunk.chunk_id == "doc-1::chunk-0"
    assert results[0].score >= 0.5
