"""Grounded prompt construction tests."""

from __future__ import annotations

from app.models import Chunk
from app.rag import REFUSAL_MESSAGE
from app.rag.prompt import build_prompt, format_context


def _chunk(title: str, text: str) -> Chunk:
    return Chunk(
        document_id="doc-1",
        chunk_id=f"{title}::0",
        source_title=title,
        source_type="synthetic",
        text=text,
        character_start=0,
        character_end=len(text),
    )


def test_format_context_numbers_and_labels_passages() -> None:
    context = format_context([_chunk("Alpha", "first"), _chunk("Beta", "second")])
    assert "[1] (Alpha) first" in context
    assert "[2] (Beta) second" in context


def test_build_prompt_includes_context_question_and_refusal_rule() -> None:
    prompt = build_prompt(
        "How are incidents reported?",
        [_chunk("Incident Response Policy", "Report incidents to the SOC.")],
    )
    assert "Report incidents to the SOC." in prompt
    assert "Incident Response Policy" in prompt
    assert "How are incidents reported?" in prompt
    assert REFUSAL_MESSAGE in prompt
