"""Provider interfaces (Protocols).

These describe the behavior the RAG core depends on, independent of the concrete
(Ollama) implementation added in a later slice.
"""

from __future__ import annotations

from typing import Protocol


class EmbeddingProvider(Protocol):
    """Produces embedding vectors for input texts."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text."""
        ...


class ChatProvider(Protocol):
    """Generates a chat completion for a grounded prompt."""

    async def generate(self, prompt: str) -> str:
        """Return the model's answer for ``prompt``."""
        ...
