#!/usr/bin/env python3
"""Ingest the synthetic demo documents so the demo corpus is populated.

Uses only the Python standard library (no dependencies). Sends each Markdown
file in sample-data/synthetic/ to the ingestion endpoint.

Usage (run through uv, per the project's uv-only rule):
    uv run --project src/ai-service python scripts/seed_demo.py [base_url]

Defaults to the ai-service at http://localhost:8000. Seeding targets the
ai-service directly because it speaks snake_case natively; the C# gateway's
public contract is camelCase, so posting snake_case fields (e.g. source_type)
through it would be dropped. Pass a gateway URL only if sending camelCase.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SYNTHETIC_DIR = REPO_ROOT / "sample-data" / "synthetic"


def title_from_filename(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").title()


def ingest(base_url: str, path: Path) -> None:
    payload = {
        "title": title_from_filename(path),
        "text": path.read_text(encoding="utf-8"),
        "source_type": "synthetic",
        "language": "en",
        "filename": path.name,
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/documents",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        body = json.loads(response.read())
    # The ai-service returns snake_case; the C# gateway returns camelCase.
    chunk_count = body.get("chunk_count", body.get("chunkCount", "?"))
    print(f"  + {payload['title']}  ({chunk_count} chunks)")


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    files = sorted(SYNTHETIC_DIR.glob("*.md"))
    if not files:
        print(f"No synthetic documents found in {SYNTHETIC_DIR}", file=sys.stderr)
        return 1

    print(f"Seeding {len(files)} document(s) into {base_url} ...")
    try:
        for path in files:
            ingest(base_url, path)
    except urllib.error.URLError as exc:
        print(f"\nCould not reach {base_url}: {exc}", file=sys.stderr)
        print("Is the stack running? (docker compose up, or run both services)", file=sys.stderr)
        return 1
    print("Done. Try asking a question at the demo page or via /ask.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
