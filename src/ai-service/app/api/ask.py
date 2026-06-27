"""Ask endpoint: evidence-based answering with citations and refusal.

Retrieves supporting chunks, builds a grounded prompt, calls the local LLM, and
returns an answer with citations - or the fixed refusal message when there is
insufficient evidence.
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    chat_provider_dependency,
    embedding_provider_dependency,
    vector_store_dependency,
)
from app.core.config import Settings, get_settings
from app.models import AnswerResponse, AskRequest
from app.providers.base import ChatProvider, EmbeddingProvider
from app.rag.answering import answer_question
from app.vectorstores.qdrant import QdrantVectorStore

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AnswerResponse)
async def ask(
    request: AskRequest,
    settings: Settings = Depends(get_settings),
    embedder: EmbeddingProvider = Depends(embedding_provider_dependency),
    vector_store: QdrantVectorStore = Depends(vector_store_dependency),
    chat_provider: ChatProvider = Depends(chat_provider_dependency),
) -> AnswerResponse:
    """Answer a question from indexed evidence, or refuse."""
    top_k = request.top_k or settings.top_k
    try:
        return await answer_question(
            request.question,
            embedder=embedder,
            vector_store=vector_store,
            chat_provider=chat_provider,
            top_k=top_k,
            min_score=settings.min_retrieval_score,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Local model error: {exc}",
        ) from exc
