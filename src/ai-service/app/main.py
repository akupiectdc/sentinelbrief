"""FastAPI application factory and wiring."""

from __future__ import annotations

from fastapi import FastAPI

from app.api import ask, documents, embeddings, health, search
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings)
    logger = get_logger("app")

    app = FastAPI(
        title="SentinelBrief AI Service",
        description="Local-only RAG core for cybersecurity documents.",
        version="0.1.0",
    )
    app.include_router(health.router)
    app.include_router(documents.router)
    app.include_router(embeddings.router)
    app.include_router(search.router)
    app.include_router(ask.router)

    logger.info(
        "ai-service started (restricted_mode=%s, llm_provider=%s, embedding_provider=%s)",
        settings.restricted_mode,
        settings.llm_provider,
        settings.embedding_provider,
    )
    return app


app = create_app()
