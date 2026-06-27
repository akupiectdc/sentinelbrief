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


def test_delete_document_removes_only_its_points() -> None:
    async def run():
        client = AsyncQdrantClient(location=":memory:")
        store = QdrantVectorStore("del", client=client)
        keep = Chunk(
            document_id="doc-2",
            chunk_id="doc-2::chunk-0",
            source_title="Keep",
            source_type="synthetic",
            text="beta",
            character_start=0,
            character_end=4,
        )
        await store.upsert([_chunk("doc-1::chunk-0", "alpha")], [[1.0, 0.0, 0.0]])
        await store.upsert([keep], [[0.0, 1.0, 0.0]])

        await store.delete_document("doc-1")

        count = await client.count("del")
        results = await store.search([0.0, 1.0, 0.0], top_k=5)
        await client.close()
        return count.count, [r.chunk.document_id for r in results]

    count, remaining = asyncio.run(run())
    assert count == 1
    assert remaining == ["doc-2"]


def test_delete_document_on_missing_collection_is_noop() -> None:
    async def run():
        client = AsyncQdrantClient(location=":memory:")
        store = QdrantVectorStore("never_created", client=client)
        await store.delete_document("doc-1")  # must not raise
        await client.close()

    asyncio.run(run())


def test_reingest_with_fewer_chunks_leaves_no_orphans() -> None:
    async def run():
        client = AsyncQdrantClient(location=":memory:")
        store = QdrantVectorStore("reingest", client=client)
        # First version: two chunks.
        await store.upsert(
            [_chunk("doc-1::chunk-0", "alpha"), _chunk("doc-1::chunk-1", "beta")],
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        )
        # Re-ingest: delete then write a single shorter chunk.
        await store.delete_document("doc-1")
        await store.upsert([_chunk("doc-1::chunk-0", "alpha")], [[1.0, 0.0, 0.0]])
        count = await client.count("reingest")
        await client.close()
        return count.count

    assert asyncio.run(run()) == 1


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
