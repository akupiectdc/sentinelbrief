"""API tests for /ask (embedder, vector store, and chat provider are faked)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.deps import (
    chat_provider_dependency,
    embedding_provider_dependency,
    vector_store_dependency,
)
from app.main import app
from app.models import Chunk
from app.rag import REFUSAL_MESSAGE
from app.vectorstores.qdrant import RetrievedChunk


class _FakeEmbedder:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class _FakeChat:
    async def generate(self, prompt: str) -> str:
        return "Report incidents to the SOC without delay [Incident Response Policy]."


def _hit() -> RetrievedChunk:
    chunk = Chunk(
        document_id="doc-1",
        chunk_id="doc-1::chunk-0",
        source_title="Incident Response Policy",
        source_type="synthetic",
        text="Report incidents to the SOC without delay.",
        character_start=0,
        character_end=42,
    )
    return RetrievedChunk(chunk=chunk, score=0.82)


def _make_vector_store(hits: list[RetrievedChunk]):
    class _FakeVectorStore:
        async def search(self, vector: list[float], top_k: int) -> list[RetrievedChunk]:
            return hits

    return _FakeVectorStore


def _override(hits: list[RetrievedChunk]) -> None:
    app.dependency_overrides[embedding_provider_dependency] = _FakeEmbedder
    app.dependency_overrides[chat_provider_dependency] = _FakeChat
    app.dependency_overrides[vector_store_dependency] = _make_vector_store(hits)


@pytest.fixture(autouse=True)
def _clear_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def test_ask_returns_grounded_answer_with_citations() -> None:
    _override([_hit()])
    client = TestClient(app)
    response = client.post("/ask", json={"question": "How are incidents reported?"})
    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is False
    assert "SOC" in body["answer"]
    assert body["citations"][0]["source_title"] == "Incident Response Policy"
    assert body["retrieved_titles"] == ["Incident Response Policy"]


def test_ask_refuses_when_no_evidence() -> None:
    _override([])
    client = TestClient(app)
    response = client.post("/ask", json={"question": "What is unrelated trivia?"})
    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is True
    assert body["answer"] == REFUSAL_MESSAGE
    assert body["citations"] == []


def test_ask_validates_input() -> None:
    _override([_hit()])
    client = TestClient(app)
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422
