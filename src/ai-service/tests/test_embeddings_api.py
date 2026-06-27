"""API tests for the embedding preview endpoint (provider is faked)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.deps import embedding_provider_dependency
from app.main import app


class _FakeEmbeddingProvider:
    """Returns a fixed-dimension vector without touching Ollama."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.5] * 16 for _ in texts]


@pytest.fixture(autouse=True)
def _override_provider() -> None:
    app.dependency_overrides[embedding_provider_dependency] = _FakeEmbeddingProvider
    yield
    app.dependency_overrides.clear()


def test_preview_returns_dimension_and_truncated_preview() -> None:
    client = TestClient(app)
    response = client.post("/embeddings/preview", json={"text": "hello world"})
    assert response.status_code == 200
    body = response.json()
    assert body["dimension"] == 16
    assert len(body["preview"]) == 8
    assert body["model"]  # configured embedding model name is reported


def test_preview_validates_input() -> None:
    client = TestClient(app)
    response = client.post("/embeddings/preview", json={"text": ""})
    assert response.status_code == 422
