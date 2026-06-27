"""Vector store abstraction (Qdrant is the local implementation)."""

from __future__ import annotations

from functools import lru_cache

from qdrant_client import AsyncQdrantClient

from app.core.config import Settings
from app.vectorstores.qdrant import QdrantVectorStore


@lru_cache
def _build_store(url: str, collection: str) -> QdrantVectorStore:
    """Build (and cache) one vector store per (url, collection)."""
    return QdrantVectorStore(collection, client=AsyncQdrantClient(url=url))


def get_vector_store(settings: Settings) -> QdrantVectorStore:
    """Return the configured Qdrant vector store."""
    return _build_store(settings.qdrant_url, settings.qdrant_collection)
