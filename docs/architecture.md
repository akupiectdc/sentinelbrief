# Architecture

SentinelBrief is split into two services plus two local infrastructure
components. The split mirrors a realistic on-premise deployment: a public-facing
gateway in C# and an AI core in Python.

## Components

| Component | Tech | Responsibility |
|-----------|------|----------------|
| `web-api` | C# ASP.NET Core Minimal API | Thin gateway. Receives client requests and forwards AI work to the ai-service. No RAG logic. |
| `ai-service` | Python FastAPI | The AI/RAG core. Parsing, chunking, embeddings, vector storage, retrieval, prompt building, answer generation. |
| Ollama | Local LLM runtime | Local chat model and embedding model. |
| Qdrant | Vector database | Stores chunk embeddings and metadata for similarity search. |

## Request flow (target)

```
client
  |  HTTP
  v
C# web-api (gateway)
  |  typed HttpClient -> AI_SERVICE_URL
  v
Python ai-service (FastAPI)
  +- parse document (TXT/MD now, PDF later)
  +- chunk text (character-based with overlap)
  +- embed chunks via Ollama
  +- upsert vectors into Qdrant
  +- retrieve top-K chunks for a question
  +- build a grounded prompt
  +- call the Ollama chat model
  \- return answer + citations + retrieval metadata
```

The C# service must remain a gateway. It must not implement RAG logic. The
Python service owns all AI/RAG behavior.

## Python module layout

```
app/
  main.py            # FastAPI app factory + startup wiring
  api/               # HTTP routes (thin; delegate to services)
  core/              # configuration, logging
  documents/         # parsing + chunking
  rag/               # retrieval, prompt building, orchestration (later)
  providers/         # LLM + embedding provider abstraction (Ollama only)
  vectorstores/      # vector store abstraction (Qdrant)
  models.py          # shared Pydantic request/response models
tests/
```

Concerns are kept separate (routes, configuration, logging, parsing, chunking,
provider abstraction, vector store abstraction, retrieval, prompt building,
answer generation, orchestration) so each can be tested in isolation.

## Configuration

All configuration comes from environment variables, documented in
`.env.example` and loaded through Pydantic Settings (`app/core/config.py`).
No service URL is hardcoded in application code.

## Restricted mode

When `RESTRICTED_MODE=true`, the ai-service only allows local providers
(`ollama`) and a local vector store (Qdrant), and rejects any cloud provider
configuration by failing fast at startup. See
[security-notes.md](security-notes.md).

## Current implementation status

Implemented: configuration, logging, health endpoint, TXT/MD parsing,
character-based chunking, shared Pydantic models, document ingestion
(`POST /documents` -> parse -> chunk -> embed -> store; plus `GET /documents` and
`GET /documents/{id}`), a local Ollama embedding provider
(`POST /embeddings/preview`), Qdrant vector storage (`QdrantVectorStore`,
cosine distance), retrieval (`POST /search`: embed query -> Qdrant top-K ->
min-score filter -> scored chunks with metadata), and evidence-based answering
(`POST /ask`: retrieve -> grounded prompt -> local Ollama chat model -> answer with
citations, or the fixed refusal when evidence is insufficient).

The C# gateway forwards `/documents` (ingest/list/get), `/search`, and `/ask` to
the ai-service via a typed HttpClient (snake_case <-> PascalCase mapping, 502 on
downstream failure), holding no RAG logic. The full local RAG flow is therefore
implemented end-to-end, through the gateway. Not implemented yet: PDF parsing.
