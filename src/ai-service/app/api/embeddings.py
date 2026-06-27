"""Embedding endpoints.

Exposes a small preview endpoint that embeds a short text via the local Ollama
provider. It is primarily for demos/debugging and requires a running Ollama
server. Vector storage and retrieval are added in later slices.
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import embedding_provider_dependency
from app.core.config import Settings, get_settings
from app.models import EmbeddingPreviewRequest, EmbeddingPreviewResponse
from app.providers.base import EmbeddingProvider

router = APIRouter(prefix="/embeddings", tags=["embeddings"])

_PREVIEW_LENGTH = 8


@router.post("/preview", response_model=EmbeddingPreviewResponse)
async def preview_embedding(
    request: EmbeddingPreviewRequest,
    settings: Settings = Depends(get_settings),
    provider: EmbeddingProvider = Depends(embedding_provider_dependency),
) -> EmbeddingPreviewResponse:
    """Embed a short text and return its dimension and a small preview."""
    try:
        vectors = await provider.embed([request.text])
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Embedding provider error: {exc}",
        ) from exc

    vector = vectors[0]
    return EmbeddingPreviewResponse(
        model=settings.ollama_embedding_model,
        dimension=len(vector),
        preview=vector[:_PREVIEW_LENGTH],
    )
