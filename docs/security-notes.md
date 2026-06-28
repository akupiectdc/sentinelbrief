# Security Notes

SentinelBrief is built with a security-aware mindset, which suits both its
cybersecurity domain and an on-premise deployment story.

## Local-only / restricted mode

The core security property is **local-only operation**. When
`RESTRICTED_MODE=true` the ai-service must:

* use only local services
* use local Ollama for LLM calls
* use local Ollama for embeddings
* use local Qdrant for vector search
* reject any cloud provider configuration
* never silently fall back to cloud APIs
* fail fast if a non-local/cloud provider is configured
* avoid external LLM, embedding, or telemetry calls

There is **no code path** for Azure OpenAI, OpenAI, Anthropic, or any other
cloud LLM provider. This is enforced by configuration validation that runs at
startup and by the absence of any cloud SDK in the dependency set.

## Secrets handling

* `.env` is git-ignored; only `.env.example` (no real values) is committed.
* The MVP requires no API keys or secrets, because every provider is local.
* CI runs without any secrets.

## Data handling

* Only synthetic documents and public source *references* are committed.
* Real, private, or large source documents stay in git-ignored local folders.
* `*.pdf` is git-ignored to avoid accidental commits of source material.

## Evidence-grounded answering

The RAG layer (once implemented) reduces hallucination risk by:

* retrieving evidence before answering
* answering only from retrieved context
* returning citations and retrieval metadata
* refusing when evidence is insufficient, with a fixed refusal message:
  *"I do not have enough evidence in the indexed documents to answer this
  question."*

## Trust boundary

The C# gateway is the only externally exposed surface in the intended
deployment. It forwards requests to the Python ai-service over the internal
network. The gateway performs no AI logic, which keeps the AI core isolated and
easier to reason about.

## Known limitations (MVP)

* No authentication/authorization on the endpoints yet.
* No rate limiting.
* Input validation is minimal beyond Pydantic model parsing.

These are acceptable for a local MVP and are listed honestly rather than hidden.
