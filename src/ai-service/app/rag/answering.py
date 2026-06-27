"""Answer orchestration: retrieve evidence, then generate a grounded answer.

Refusal happens in two places:
* before the LLM, when no chunk clears the score threshold (no evidence), and
* after the LLM, when the model emits the refusal sentence itself.
"""

from __future__ import annotations

from app.models import AnswerResponse, Citation
from app.providers.base import ChatProvider, EmbeddingProvider
from app.rag import REFUSAL_MESSAGE
from app.rag.prompt import build_prompt
from app.rag.retrieval import retrieve
from app.vectorstores.qdrant import QdrantVectorStore, RetrievedChunk


def _unique_titles(hits: list[RetrievedChunk]) -> list[str]:
    titles: list[str] = []
    for hit in hits:
        if hit.chunk.source_title not in titles:
            titles.append(hit.chunk.source_title)
    return titles


def _citations(hits: list[RetrievedChunk]) -> list[Citation]:
    return [
        Citation(
            source_title=hit.chunk.source_title,
            chunk_id=hit.chunk.chunk_id,
            score=hit.score,
            page_number=hit.chunk.page_number,
        )
        for hit in hits
    ]


async def answer_question(
    question: str,
    *,
    embedder: EmbeddingProvider,
    vector_store: QdrantVectorStore,
    chat_provider: ChatProvider,
    top_k: int,
    min_score: float,
) -> AnswerResponse:
    """Retrieve evidence and produce a grounded answer, or refuse."""
    hits = await retrieve(
        question,
        embedder=embedder,
        vector_store=vector_store,
        top_k=top_k,
        min_score=min_score,
    )

    # No evidence cleared the threshold: refuse without calling the LLM.
    if not hits:
        return AnswerResponse(
            answer=REFUSAL_MESSAGE,
            citations=[],
            retrieved_titles=[],
            refused=True,
        )

    prompt = build_prompt(question, [hit.chunk for hit in hits])
    raw_answer = (await chat_provider.generate(prompt)).strip()

    refused = raw_answer == "" or REFUSAL_MESSAGE.lower() in raw_answer.lower()
    if refused:
        return AnswerResponse(
            answer=REFUSAL_MESSAGE,
            citations=[],
            retrieved_titles=_unique_titles(hits),
            refused=True,
        )

    return AnswerResponse(
        answer=raw_answer,
        citations=_citations(hits),
        retrieved_titles=_unique_titles(hits),
        refused=False,
    )
