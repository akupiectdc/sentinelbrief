"""Health endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.models import HealthResponse, InfoResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Report service health and whether restricted mode is enabled."""
    return HealthResponse(restricted_mode=settings.restricted_mode)


@router.get("/info", response_model=InfoResponse)
def info(settings: Settings = Depends(get_settings)) -> InfoResponse:
    """Report non-secret runtime configuration (used by the demo banner)."""
    return InfoResponse(
        restricted_mode=settings.restricted_mode,
        llm_provider=settings.llm_provider,
        embedding_provider=settings.embedding_provider,
        chat_model=settings.ollama_chat_model,
        embedding_model=settings.ollama_embedding_model,
    )
