"""Document parsing for TXT and Markdown.

PDF parsing (via PyMuPDF) is a planned later slice and is intentionally not
implemented here.
"""

from __future__ import annotations

from pathlib import Path

SUPPORTED_SUFFIXES: set[str] = {".txt", ".md", ".markdown"}


def parse_text(raw: str) -> str:
    """Normalize raw text: unify newlines and strip surrounding whitespace."""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip()


def parse_file(path: Path) -> str:
    """Parse a supported text file into normalized plain text."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        supported = sorted(SUPPORTED_SUFFIXES)
        raise ValueError(f"Unsupported file type '{suffix}'. Supported: {supported}.")
    return parse_text(path.read_text(encoding="utf-8"))
