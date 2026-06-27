"""Provider selection/validation tests."""

from __future__ import annotations

import pytest

from app.providers import validate_provider


def test_validate_provider_accepts_ollama() -> None:
    assert validate_provider("ollama") == "ollama"
    assert validate_provider("OLLAMA") == "ollama"


@pytest.mark.parametrize("provider", ["openai", "azure_openai", "anthropic"])
def test_validate_provider_rejects_cloud(provider: str) -> None:
    with pytest.raises(ValueError):
        validate_provider(provider)
