"""Ollama embedding provider tests (no real Ollama; httpx is mocked)."""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from app.providers.ollama import OllamaEmbeddingProvider


def _provider_with_handler(handler) -> tuple[OllamaEmbeddingProvider, httpx.AsyncClient]:
    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, base_url="http://ollama-test")
    provider = OllamaEmbeddingProvider("http://ollama-test", "nomic-embed-text", client=client)
    return provider, client


def test_embed_returns_one_vector_per_text() -> None:
    seen_models: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        seen_models.append(body["model"])
        assert request.url.path == "/api/embeddings"
        return httpx.Response(200, json={"embedding": [0.1, 0.2, 0.3]})

    provider, client = _provider_with_handler(handler)

    async def run() -> list[list[float]]:
        try:
            return await provider.embed(["alpha", "beta"])
        finally:
            await client.aclose()

    vectors = asyncio.run(run())

    assert vectors == [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]
    assert seen_models == ["nomic-embed-text", "nomic-embed-text"]


def test_embed_raises_on_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    provider, client = _provider_with_handler(handler)

    async def run() -> None:
        try:
            await provider.embed(["alpha"])
        finally:
            await client.aclose()

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(run())
