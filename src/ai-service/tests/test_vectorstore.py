"""Qdrant vector store tests using the in-memory client (no server)."""

from __future__ import annotations

import asyncio

from qdrant_client import AsyncQdrantClient

from app.models import Chunk
from app.vectorstores.qdrant import QdrantVectorStore


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


def test_upsert_then_search_returns_nearest_chunk() -> None:
    async def run():
        client = AsyncQdrantClient(location=":memory:")
        store = QdrantVectorStore("test_collection", client=client)
        chunks = [_chunk("doc-1::chunk-0", "alpha"), _chunk("doc-1::chunk-1", "beta")]
        vectors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
        await store.upsert(chunks, vectors)

        results = await store.search([0.9, 0.1, 0.0], top_k=1)
        await client.close()
        return results

    results = asyncio.run(run())
    assert len(results) == 1
    assert results[0].chunk.chunk_id == "doc-1::chunk-0"
    assert results[0].score > 0.5


def test_search_on_missing_collection_returns_empty() -> None:
    async def run():
        client = AsyncQdrantClient(location=":memory:")
        store = QdrantVectorStore("never_created", client=client)
        results = await store.search([0.1, 0.2, 0.3], top_k=5)
        await client.close()
        return results

    assert asyncio.run(run()) == []


def test_upsert_is_idempotent_by_chunk_id() -> None:
    async def run():
        client = AsyncQdrantClient(location=":memory:")
        store = QdrantVectorStore("idem", client=client)
        chunk = _chunk("doc-1::chunk-0", "alpha")
        await store.upsert([chunk], [[1.0, 0.0, 0.0]])
        await store.upsert([chunk], [[1.0, 0.0, 0.0]])
        count = await client.count("idem")
        await client.close()
        return count.count

    assert asyncio.run(run()) == 1
