"""API tests for the /search endpoint (embedder + vector store are faked)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.deps import embedding_provider_dependency, vector_store_dependency
from app.main import app
from app.models import Chunk
from app.vectorstores.qdrant import RetrievedChunk


class _FakeEmbedder:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class _FakeVectorStore:
    """Returns preset hits; records the requested top_k."""

    def __init__(self) -> None:
        self.last_top_k: int | None = None

    async def search(self, vector: list[float], top_k: int) -> list[RetrievedChunk]:
        self.last_top_k = top_k
        chunk = Chunk(
            document_id="doc-1",
            chunk_id="doc-1::chunk-0",
            source_title="Incident Response Policy",
            source_type="synthetic",
            text="Report incidents to the SOC without delay.",
            character_start=0,
            character_end=42,
        )
        return [RetrievedChunk(chunk=chunk, score=0.91)]


@pytest.fixture
def fake_store() -> _FakeVectorStore:
    store = _FakeVectorStore()
    app.dependency_overrides[embedding_provider_dependency] = _FakeEmbedder
    app.dependency_overrides[vector_store_dependency] = lambda: store
    yield store
    app.dependency_overrides.clear()


def test_search_returns_results_with_metadata(fake_store: _FakeVectorStore) -> None:
    client = TestClient(app)
    response = client.post("/search", json={"query": "How are incidents reported?"})
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "How are incidents reported?"
    assert body["count"] == 1
    result = body["results"][0]
    assert result["chunk_id"] == "doc-1::chunk-0"
    assert result["source_title"] == "Incident Response Policy"
    assert result["score"] == 0.91


def test_search_uses_requested_top_k(fake_store: _FakeVectorStore) -> None:
    client = TestClient(app)
    client.post("/search", json={"query": "anything", "top_k": 3})
    assert fake_store.last_top_k == 3


def test_search_validates_input(fake_store: _FakeVectorStore) -> None:
    client = TestClient(app)
    response = client.post("/search", json={"query": ""})
    assert response.status_code == 422
