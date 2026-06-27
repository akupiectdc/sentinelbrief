"""API tests for document ingestion endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.deps import embedding_provider_dependency, vector_store_dependency
from app.documents.store import get_document_store
from app.main import app

client = TestClient(app)


class _FakeEmbeddingProvider:
    """Returns a fixed vector per chunk; never touches Ollama."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class _FakeVectorStore:
    """Records upserts and deletes in memory; never touches Qdrant."""

    def __init__(self) -> None:
        self.upserted: list[tuple] = []
        self.deleted: list[str] = []

    async def upsert(self, chunks, vectors) -> None:
        self.upserted.append((chunks, vectors))

    async def delete_document(self, document_id) -> None:
        self.deleted.append(document_id)


@pytest.fixture(autouse=True)
def _isolate_dependencies() -> None:
    get_document_store().clear()
    app.dependency_overrides[embedding_provider_dependency] = _FakeEmbeddingProvider
    app.dependency_overrides[vector_store_dependency] = _FakeVectorStore
    yield
    app.dependency_overrides.clear()
    get_document_store().clear()


def _ingest(title: str = "Phishing Triage Playbook") -> dict:
    payload = {
        "title": title,
        "text": "When a phishing email is reported, acknowledge it. " * 40,
        "source_type": "synthetic",
        "language": "en",
    }
    response = client.post("/documents", json=payload)
    assert response.status_code == 201
    return response.json()


def test_ingest_returns_metadata_with_chunk_count() -> None:
    body = _ingest()
    assert body["title"] == "Phishing Triage Playbook"
    assert body["source_type"] == "synthetic"
    assert body["chunk_count"] >= 1
    assert "document_id" in body
    assert "ingested_at" in body


def test_list_documents_reflects_ingestion() -> None:
    _ingest("Doc A")
    _ingest("Doc B")
    response = client.get("/documents")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    titles = {d["title"] for d in body["documents"]}
    assert titles == {"Doc A", "Doc B"}


def test_reingesting_same_document_updates_in_place() -> None:
    # Same source identity (same title, no filename) must map to one document,
    # not accumulate duplicates on re-ingest.
    first = _ingest("Same Doc")
    second = _ingest("Same Doc")
    assert first["document_id"] == second["document_id"]

    response = client.get("/documents")
    assert response.json()["count"] == 1


def test_distinct_sources_stay_separate() -> None:
    a = _ingest("Doc A")
    b = _ingest("Doc B")
    assert a["document_id"] != b["document_id"]
    assert client.get("/documents").json()["count"] == 2


def test_get_document_returns_chunks() -> None:
    document_id = _ingest()["document_id"]
    response = client.get(f"/documents/{document_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["document"]["document_id"] == document_id
    assert len(body["chunks"]) == body["document"]["chunk_count"]


def test_get_unknown_document_returns_404() -> None:
    response = client.get("/documents/does-not-exist")
    assert response.status_code == 404


def test_ingest_validates_input() -> None:
    response = client.post("/documents", json={"title": "", "text": ""})
    assert response.status_code == 422
