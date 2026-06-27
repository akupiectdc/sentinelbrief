"""Qdrant-backed vector store.

Stores chunk embeddings (and chunk metadata as payload) and performs similarity
search. The Qdrant client is injected so tests can use the in-memory mode
(``location=":memory:"``) without a running server.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from qdrant_client import AsyncQdrantClient
from qdrant_client import models as qmodels

from app.models import Chunk

# Deterministic namespace so re-ingesting the same chunk overwrites its point.
_POINT_NAMESPACE = uuid.UUID("6f9619ff-8b86-d011-b42d-00cf4fc964ff")


@dataclass
class RetrievedChunk:
    """A chunk returned from a similarity search, with its score."""

    chunk: Chunk
    score: float


def _point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(_POINT_NAMESPACE, chunk_id))


class QdrantVectorStore:
    """Vector store implementation backed by Qdrant."""

    def __init__(self, collection: str, *, client: AsyncQdrantClient) -> None:
        self._collection = collection
        self._client = client

    async def ensure_collection(self, vector_size: int) -> None:
        """Create the collection (cosine distance) if it does not exist."""
        if not await self._client.collection_exists(self._collection):
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=qmodels.Distance.COSINE,
                ),
            )

    async def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Insert or update chunk vectors and their metadata payloads."""
        if not chunks:
            return
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")

        await self.ensure_collection(len(vectors[0]))
        points = [
            qmodels.PointStruct(
                id=_point_id(chunk.chunk_id),
                vector=vector,
                payload=chunk.model_dump(),
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        await self._client.upsert(collection_name=self._collection, points=points)

    async def delete_document(self, document_id: str) -> None:
        """Delete every stored point belonging to ``document_id``.

        Called before re-ingesting a document so the new version replaces the
        old chunks instead of leaving stale duplicates behind (including the
        case where the new version has fewer chunks than before).
        """
        if not await self._client.collection_exists(self._collection):
            return
        await self._client.delete(
            collection_name=self._collection,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )

    async def search(self, vector: list[float], top_k: int) -> list[RetrievedChunk]:
        """Return the ``top_k`` most similar chunks to ``vector``."""
        if not await self._client.collection_exists(self._collection):
            return []
        response = await self._client.query_points(
            collection_name=self._collection,
            query=vector,
            limit=top_k,
            with_payload=True,
        )
        return [
            RetrievedChunk(chunk=Chunk(**point.payload), score=point.score)
            for point in response.points
        ]
