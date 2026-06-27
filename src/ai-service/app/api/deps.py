"""Shared FastAPI dependencies.

Centralizing these lets routes share the same dependency callables and lets
tests override them (e.g. to inject fakes for the embedding provider or vector
store) without touching real Ollama or Qdrant.
"""

from __future__ import annotations

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.providers import get_chat_provider, get_embedding_provider
from app.providers.base import ChatProvider, EmbeddingProvider
from app.vectorstores import get_vector_store
from app.vectorstores.qdrant import QdrantVectorStore


def embedding_provider_dependency(
    settings: Settings = Depends(get_settings),
) -> EmbeddingProvider:
    """Provide the configured embedding provider."""
    return get_embedding_provider(settings)


def chat_provider_dependency(
    settings: Settings = Depends(get_settings),
) -> ChatProvider:
    """Provide the configured chat provider."""
    return get_chat_provider(settings)


def vector_store_dependency(
    settings: Settings = Depends(get_settings),
) -> QdrantVectorStore:
    """Provide the configured Qdrant vector store."""
    return get_vector_store(settings)
