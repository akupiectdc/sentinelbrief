"""Retrieval: embed a query, search the vector store, filter by score.

This is the first half of the RAG flow. The grounded prompt + answer generation
(``/ask``) build on top of these retrieved chunks in a later slice.
"""

from __future__ import annotations

from app.providers.base import EmbeddingProvider
from app.vectorstores.qdrant import QdrantVectorStore, RetrievedChunk


async def retrieve(
    query: str,
    *,
    embedder: EmbeddingProvider,
    vector_store: QdrantVectorStore,
    top_k: int,
    min_score: float,
) -> list[RetrievedChunk]:
    """Return chunks similar to ``query`` whose score meets ``min_score``.

    Results are ordered most-similar first (as returned by the vector store).
    """
    query_vectors = await embedder.embed([query])
    hits = await vector_store.search(query_vectors[0], top_k)
    return [hit for hit in hits if hit.score >= min_score]
