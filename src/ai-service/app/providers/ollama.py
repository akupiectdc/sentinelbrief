"""Local Ollama embedding provider.

Calls the local Ollama HTTP API to produce embedding vectors. This is the only
embedding provider in the MVP. No cloud SDK is involved.
"""

from __future__ import annotations

import httpx

_DEFAULT_TIMEOUT = 30.0
_DEFAULT_CHAT_TIMEOUT = 120.0


class OllamaEmbeddingProvider:
    """Embedding provider backed by a local Ollama server."""

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        client: httpx.AsyncClient | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._client = client
        self._timeout = timeout

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text.

        Uses Ollama's ``/api/embeddings`` endpoint (one request per text).
        """
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self._timeout)
        try:
            vectors: list[list[float]] = []
            for text in texts:
                response = await client.post(
                    f"{self._base_url}/api/embeddings",
                    json={"model": self._model, "prompt": text},
                )
                response.raise_for_status()
                payload = response.json()
                vectors.append(payload["embedding"])
            return vectors
        finally:
            if owns_client:
                await client.aclose()


class OllamaChatProvider:
    """Chat-completion provider backed by a local Ollama server."""

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        client: httpx.AsyncClient | None = None,
        timeout: float = _DEFAULT_CHAT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._client = client
        self._timeout = timeout

    async def generate(self, prompt: str) -> str:
        """Return the model's completion for ``prompt`` (non-streaming)."""
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self._timeout)
        try:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            payload = response.json()
            return payload["response"]
        finally:
            if owns_client:
                await client.aclose()
