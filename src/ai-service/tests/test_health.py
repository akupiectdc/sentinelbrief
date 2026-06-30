"""API tests for health and chunking endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "ai-service"
    assert "restricted_mode" in body


def test_info_endpoint_reports_configured_models() -> None:
    response = client.get("/info")
    assert response.status_code == 200
    body = response.json()
    assert body["chat_model"]
    assert body["embedding_model"]
    assert body["llm_provider"]
    assert isinstance(body["restricted_mode"], bool)


def test_chunk_endpoint_returns_chunks() -> None:
    payload = {
        "title": "Incident Response Policy",
        "text": "This is a sample security procedure. " * 60,
        "source_type": "synthetic",
    }
    response = client.post("/documents/chunk", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Incident Response Policy"
    assert body["chunk_count"] >= 1
    assert body["chunk_count"] == len(body["chunks"])
    assert body["chunks"][0]["source_title"] == "Incident Response Policy"


def test_chunk_endpoint_validates_input() -> None:
    response = client.post("/documents/chunk", json={"title": "", "text": ""})
    assert response.status_code == 422
