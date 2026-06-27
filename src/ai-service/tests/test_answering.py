"""Answer-orchestration tests with fakes (no Ollama, no Qdrant)."""

from __future__ import annotations

import asyncio

from app.models import Chunk
from app.rag import REFUSAL_MESSAGE
from app.rag.answering import answer_question
from app.vectorstores.qdrant import RetrievedChunk


class _FakeEmbedder:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class _FakeVectorStore:
    def __init__(self, hits: list[RetrievedChunk]) -> None:
        self._hits = hits

    async def search(self, vector: list[float], top_k: int) -> list[RetrievedChunk]:
        return self._hits


class _FakeChat:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.called = False

    async def generate(self, prompt: str) -> str:
        self.called = True
        return self.reply


def _hit(title: str, text: str, score: float) -> RetrievedChunk:
    chunk = Chunk(
        document_id="doc-1",
        chunk_id=f"{title}::0",
        source_title=title,
        source_type="synthetic",
        text=text,
        character_start=0,
        character_end=len(text),
    )
    return RetrievedChunk(chunk=chunk, score=score)


def _answer(store: _FakeVectorStore, chat: _FakeChat, *, min_score: float = 0.25):
    return asyncio.run(
        answer_question(
            "How are incidents reported?",
            embedder=_FakeEmbedder(),
            vector_store=store,
            chat_provider=chat,
            top_k=5,
            min_score=min_score,
        )
    )


def test_refuses_without_evidence_and_skips_llm() -> None:
    chat = _FakeChat("this must not be used")
    response = _answer(_FakeVectorStore([]), chat)
    assert response.refused is True
    assert response.answer == REFUSAL_MESSAGE
    assert response.citations == []
    assert chat.called is False


def test_grounded_answer_includes_citations() -> None:
    hits = [_hit("Incident Response Policy", "Report incidents to the SOC.", 0.82)]
    chat = _FakeChat("Report incidents to the SOC without delay [Incident Response Policy].")
    response = _answer(_FakeVectorStore(hits), chat)
    assert response.refused is False
    assert "SOC" in response.answer
    assert response.citations[0].source_title == "Incident Response Policy"
    assert response.citations[0].score == 0.82
    assert response.retrieved_titles == ["Incident Response Policy"]
    assert chat.called is True


def test_model_refusal_is_honored() -> None:
    hits = [_hit("Some Doc", "unrelated text", 0.3)]
    chat = _FakeChat(REFUSAL_MESSAGE)
    response = _answer(_FakeVectorStore(hits), chat, min_score=0.0)
    assert response.refused is True
    assert response.answer == REFUSAL_MESSAGE
    assert response.citations == []
