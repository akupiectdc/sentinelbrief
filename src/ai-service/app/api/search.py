"""Search endpoint: similarity retrieval over indexed chunks.

Exposes retrieval metadata (scores, source titles, chunk IDs) for debugging and
demos. Requires a running Ollama (to embed the query) and Qdrant.
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import embedding_provider_dependency, vector_store_dependency
from app.core.config import Settings, get_settings
from app.models import RetrievedChunkResult, SearchRequest, SearchResponse
from app.providers.base import EmbeddingProvider
from app.rag.retrieval import retrieve
from app.vectorstores.qdrant import QdrantVectorStore

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    settings: Settings = Depends(get_settings),
    embedder: EmbeddingProvider = Depends(embedding_provider_dependency),
    vector_store: QdrantVectorStore = Depends(vector_store_dependency),
) -> SearchResponse:
    """Retrieve the chunks most similar to the query."""
    top_k = request.top_k or settings.top_k
    try:
        hits = await retrieve(
            request.query,
            embedder=embedder,
            vector_store=vector_store,
            top_k=top_k,
            min_score=settings.min_retrieval_score,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Embedding provider error: {exc}",
        ) from exc

    results = [
        RetrievedChunkResult(
            chunk_id=hit.chunk.chunk_id,
            document_id=hit.chunk.document_id,
            source_title=hit.chunk.source_title,
            source_type=hit.chunk.source_type,
            text=hit.chunk.text,
            score=hit.score,
            page_number=hit.chunk.page_number,
        )
        for hit in hits
    ]
    return SearchResponse(query=request.query, count=len(results), results=results)
