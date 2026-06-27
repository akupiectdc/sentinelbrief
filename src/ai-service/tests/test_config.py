"""Configuration loading tests."""

from __future__ import annotations

import pytest

from app.core.config import Settings


def test_defaults_load() -> None:
    settings = Settings(_env_file=None)
    assert settings.restricted_mode is True
    assert settings.llm_provider == "ollama"
    assert settings.embedding_provider == "ollama"
    assert settings.chunk_size == 900
    assert settings.chunk_overlap == 150
    assert settings.top_k == 5


def test_chunk_overlap_must_be_smaller_than_size() -> None:
    with pytest.raises(ValueError):
        Settings(_env_file=None, chunk_size=100, chunk_overlap=100)
