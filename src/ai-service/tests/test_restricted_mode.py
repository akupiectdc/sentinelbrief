"""Restricted-mode behavior tests."""

from __future__ import annotations

import pytest

from app.core.config import Settings


def test_restricted_rejects_cloud_llm_provider() -> None:
    with pytest.raises(ValueError):
        Settings(_env_file=None, restricted_mode=True, llm_provider="openai")


def test_restricted_rejects_cloud_embedding_provider() -> None:
    with pytest.raises(ValueError):
        Settings(_env_file=None, restricted_mode=True, embedding_provider="azure_openai")


def test_restricted_allows_local_ollama() -> None:
    settings = Settings(
        _env_file=None,
        restricted_mode=True,
        llm_provider="ollama",
        embedding_provider="ollama",
    )
    assert settings.llm_provider == "ollama"
    assert settings.embedding_provider == "ollama"


def test_non_restricted_does_not_enforce_local_providers() -> None:
    settings = Settings(_env_file=None, restricted_mode=False, llm_provider="something-else")
    assert settings.restricted_mode is False
    assert settings.llm_provider == "something-else"
