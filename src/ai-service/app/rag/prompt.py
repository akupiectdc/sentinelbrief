"""Grounded prompt construction.

The prompt instructs the model to answer strictly from the retrieved context,
cite sources, and emit the exact refusal sentence when the context is
insufficient. Keeping this in one place makes the answering behavior testable.
"""

from __future__ import annotations

from app.models import Chunk
from app.rag import REFUSAL_MESSAGE

_SYSTEM_INSTRUCTIONS = (
    "You are SentinelBrief, a cybersecurity assistant. Answer the question using "
    "ONLY the numbered context passages below. Do not use outside knowledge. "
    "Cite the passages you use by their source title in square brackets, e.g. "
    "[Incident Response Policy]. If the context does not contain enough "
    "information to answer, reply with EXACTLY this sentence and nothing else:\n"
    f"{REFUSAL_MESSAGE}"
)


def format_context(chunks: list[Chunk]) -> str:
    """Render retrieved chunks as a numbered, source-labelled context block."""
    lines: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        lines.append(f"[{index}] ({chunk.source_title}) {chunk.text}")
    return "\n\n".join(lines)


def build_prompt(question: str, chunks: list[Chunk]) -> str:
    """Build the full grounded prompt from the question and retrieved chunks."""
    context = format_context(chunks)
    return (
        f"{_SYSTEM_INSTRUCTIONS}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )
