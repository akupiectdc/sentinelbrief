# Demo Script

A short walk-through of SentinelBrief's local RAG flow, end-to-end. The fastest
way to see it is the web page (below).

## 0. Setup

```bash
cp .env.example .env
docker compose up --build
docker compose exec ollama ollama pull llama3.1:8b
docker compose exec ollama ollama pull nomic-embed-text
```

Or run the services directly (no Docker) for a quick demo:

```bash
# terminal 1
cd src/ai-service && uv sync && uv run uvicorn app.main:app --port 8000

# terminal 2
cd src/web-api && dotnet run --project SentinelBrief.WebApi
```

Seed the synthetic demo corpus so questions have evidence to draw on:

```bash
uv run --project src/ai-service python scripts/seed_demo.py
```

## Web demo page (recommended)

Open <http://localhost:8080>. The gateway serves a single dark "security
console" page: type a question (or click an example) and it shows the grounded
answer with citation cards (source title, chunk id, score), a loading state, and
a distinct refusal state. This is the easiest, most visual way to demo the tool.

## 1. Health checks (works now)

```bash
curl http://localhost:8000/health
curl http://localhost:8080/health
```

Note: the C# gateway and the Python AI core are separate services; the
gateway forwards work to the AI core.

## 2. Chunking preview (works now)

The ai-service can parse and chunk a TXT/Markdown document. Point at one of the
synthetic procedures:

```bash
curl -X POST http://localhost:8000/documents/chunk \
  -H "Content-Type: application/json" \
  -d '{"title":"Incident Response Policy","text":"...paste content...","source_type":"synthetic"}'
```

Note: deterministic, character-based chunking with overlap and chunk
metadata, ready to be embedded.

## 3. Ingest a document (works now)

```bash
# ingest a synthetic procedure into the ai-service (in-memory store)
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{"title":"Phishing Triage Playbook","text":"...paste content...","source_type":"synthetic"}'

# list ingested documents
curl http://localhost:8000/documents
```

Note: parse -> chunk -> embed (Ollama) -> store vectors in Qdrant,
returning document metadata (`document_id`, `ingested_at`, `chunk_count`). You
can show the stored vectors in the Qdrant dashboard at
<http://localhost:6333/dashboard>.

## 4. Embedding preview (works now; requires Ollama)

```bash
curl -X POST http://localhost:8000/embeddings/preview \
  -H "Content-Type: application/json" \
  -d '{"text":"How should a phishing email be triaged?"}'
```

Note: chunks are embedded locally via Ollama through the provider
abstraction. Response reports the model, vector dimension, and a short preview.
Storing these vectors in Qdrant is the next slice.

## 5. Retrieval / search (works now; requires Ollama + Qdrant)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"How should security incidents be reported?","top_k":3}'
```

Note: the query is embedded locally, Qdrant returns the most similar
chunks, results below `MIN_RETRIEVAL_SCORE` are dropped, and the response
exposes scores + source titles + chunk IDs (the retrieval metadata). This is the
evidence that the `/ask` answer will be built from.

## 6. Ask a grounded question (works now; requires Ollama + Qdrant)

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How should security incidents be reported?"}'
```

The response contains an `answer`, `citations` (source titles, chunk IDs,
scores), `retrieved_titles`, and a `refused` flag. The answer is grounded in the
retrieved chunks and cites its sources.

The same endpoints are available through the **C# gateway** on port 8080 - it
forwards to the ai-service and adds no RAG logic. Swap the port to demo the full
two-service path:

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How should security incidents be reported?"}'
```

## 7. Refusal demo (works now)

Ask something the corpus does not cover:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What was the closing price of a stock yesterday?"}'
```

Expected: `refused: true` and the answer *"I do not have enough evidence in the
indexed documents to answer this question."*

Note: the system refuses rather than hallucinating - a key property for
a security intelligence tool. Refusal triggers either when no chunk clears
`MIN_RETRIEVAL_SCORE` or when the grounded model declines.

## Recording a demo GIF

A short GIF on the web page makes the repo "clickable" at a glance.

1. Start the stack and seed the corpus (steps 0 above).
2. Open <http://localhost:8080> in a clean browser window (hide bookmarks).
3. Start a screen recording of just the browser window (macOS: `Cmd-Shift-5`).
4. Record this sequence, slowly:
   * click the "incidents" example -> show the grounded answer + citation cards;
   * click the "phishing" example -> show another grounded answer;
   * type an out-of-corpus question (e.g. a stock price) -> show the refusal state.
5. Trim to ~15-25 seconds and export as GIF (e.g. with Gifski or `ffmpeg`).
6. Save it to `docs/assets/demo.gif` and reference it from `README.md`.
