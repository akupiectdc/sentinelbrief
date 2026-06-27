"""Document parsing tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.documents.parsing import parse_file, parse_text


def test_parse_text_normalizes_newlines() -> None:
    assert parse_text("a\r\nb\r\nc\r\n") == "a\nb\nc"


def test_parse_text_strips_surrounding_whitespace() -> None:
    assert parse_text("  \n hello \n ") == "hello"


def test_parse_file_reads_markdown(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("# Title\n\nBody text", encoding="utf-8")
    assert "Title" in parse_file(path)


def test_parse_file_rejects_unsupported_type(tmp_path: Path) -> None:
    path = tmp_path / "doc.pdf"
    path.write_text("not parsed", encoding="utf-8")
    with pytest.raises(ValueError):
        parse_file(path)
