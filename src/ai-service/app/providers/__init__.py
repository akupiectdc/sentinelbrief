"""LLM and embedding provider abstraction.

Only local Ollama is allowed in the MVP. The concrete embedding client lives in
``app.providers.ollama``; this package exposes validation and a factory.
"""

from __future__ import annotations

from app.core.config import Settings
from app.providers.base import ChatProvider, EmbeddingProvider
from app.providers.ollama import OllamaChatProvider, OllamaEmbeddingProvider

SUPPORTED_PROVIDERS: set[str] = {"ollama"}


def validate_provider(provider: str) -> str:
    """Return the normalized provider name, or raise for unsupported providers."""
    normalized = provider.lower()
    if normalized not in SUPPORTED_PROVIDERS:
        supported = sorted(SUPPORTED_PROVIDERS)
        raise ValueError(f"Unsupported provider '{provider}'. Supported: {supported}.")
    return normalized


def get_embedding_provider(settings: Settings) -> EmbeddingProvider:
    """Build the configured embedding provider (Ollama only in the MVP)."""
    provider = validate_provider(settings.embedding_provider)
    if provider == "ollama":
        return OllamaEmbeddingProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
        )
    # Unreachable while SUPPORTED_PROVIDERS == {"ollama"}; kept for clarity.
    raise ValueError(f"No embedding provider implementation for '{provider}'.")


def get_chat_provider(settings: Settings) -> ChatProvider:
    """Build the configured chat provider (Ollama only in the MVP)."""
    provider = validate_provider(settings.llm_provider)
    if provider == "ollama":
        return OllamaChatProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_chat_model,
        )
    # Unreachable while SUPPORTED_PROVIDERS == {"ollama"}; kept for clarity.
    raise ValueError(f"No chat provider implementation for '{provider}'.")
