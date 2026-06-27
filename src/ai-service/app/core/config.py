"""Application configuration loaded from environment variables.

All configuration is read from the environment (and an optional local ``.env``
file). No service URL is hardcoded in application code. When restricted mode is
enabled, only local providers are accepted and the service fails fast on any
cloud provider configuration.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The only providers allowed in the MVP. Restricted mode enforces these.
LOCAL_PROVIDERS: set[str] = {"ollama"}


class Settings(BaseSettings):
    """Typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Local-only restricted mode.
    restricted_mode: bool = True

    # Providers (only "ollama" is implemented in the MVP).
    llm_provider: str = "ollama"
    embedding_provider: str = "ollama"

    # Local Ollama.
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.1:8b"
    ollama_embedding_model: str = "nomic-embed-text"

    # Local Qdrant.
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "sentinelbrief_documents"

    # ai-service binding.
    ai_service_host: str = "0.0.0.0"
    ai_service_port: int = 8000
    ai_service_url: str = "http://localhost:8000"

    # web-api (informational; used by the C# gateway).
    web_api_port: int = 5000
    web_api_url: str = "http://localhost:5000"

    # Retrieval tuning.
    top_k: int = 5
    min_retrieval_score: float = 0.25

    # Chunking.
    chunk_size: int = 900
    chunk_overlap: int = 150

    # Logging.
    log_level: str = "INFO"

    @model_validator(mode="after")
    def _validate(self) -> Settings:
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")

        if self.restricted_mode:
            for name, provider in (
                ("LLM_PROVIDER", self.llm_provider),
                ("EMBEDDING_PROVIDER", self.embedding_provider),
            ):
                if provider.lower() not in LOCAL_PROVIDERS:
                    allowed = sorted(LOCAL_PROVIDERS)
                    raise ValueError(
                        f"RESTRICTED_MODE is enabled but {name}='{provider}' is not a "
                        f"local provider. Allowed local providers: {allowed}."
                    )
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
