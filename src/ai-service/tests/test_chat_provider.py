"""Ollama chat provider tests (no real Ollama; httpx is mocked)."""

from __future__ import annotations

import asyncio
import json

import httpx

from app.providers.ollama import OllamaChatProvider


def test_generate_returns_model_response() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        assert request.url.path == "/api/generate"
        return httpx.Response(200, json={"response": "Report incidents to the SOC."})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://t")
    provider = OllamaChatProvider("http://t", "llama3.1:8b", client=client)

    async def run() -> str:
        try:
            return await provider.generate("some grounded prompt")
        finally:
            await client.aclose()

    answer = asyncio.run(run())
    assert answer == "Report incidents to the SOC."
    assert captured["model"] == "llama3.1:8b"
    assert captured["stream"] is False
