"""RAG orchestration: retrieval, prompt building, answer generation.

These slices are implemented later. The fixed refusal message lives here so the
whole service shares a single source of truth.
"""

from __future__ import annotations

REFUSAL_MESSAGE = (
    "I do not have enough evidence in the indexed documents to answer this question."
)
