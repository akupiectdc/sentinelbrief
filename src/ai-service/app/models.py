"""Shared Pydantic request/response models.

These models define the service's data contract. Some models (citations,
answers) describe the target RAG contract and are not yet produced by an
endpoint in this skeleton.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: str = "ok"
    service: str = "ai-service"
    restricted_mode: bool


class InfoResponse(BaseModel):
    """Non-secret runtime configuration (for the demo banner and debugging)."""

    restricted_mode: bool
    llm_provider: str
    embedding_provider: str
    chat_model: str
    embedding_model: str


class ChunkRequest(BaseModel):
    """Request to parse and chunk a document's text."""

    title: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    source_type: str = "user"
    language: str = "en"


class Chunk(BaseModel):
    """A single text chunk with its source metadata."""

    document_id: str
    chunk_id: str
    source_title: str
    source_type: str
    text: str
    character_start: int
    character_end: int
    page_number: int | None = None


class ChunkResponse(BaseModel):
    """Result of chunking a document."""

    document_id: str
    title: str
    chunk_count: int
    chunks: list[Chunk]


# --- Target RAG contract (not yet implemented) -----------------------------


class Citation(BaseModel):
    """A citation pointing back to a retrieved chunk."""

    source_title: str
    chunk_id: str
    score: float | None = None
    page_number: int | None = None


class AskRequest(BaseModel):
    """A grounded question to answer from indexed evidence."""

    question: str = Field(..., min_length=1)
    top_k: int | None = None


class AnswerResponse(BaseModel):
    """An evidence-based answer, or a refusal."""

    answer: str
    citations: list[Citation] = []
    retrieved_titles: list[str] = []
    refused: bool = False


# --- Document ingestion (slice 2) ------------------------------------------


class IngestRequest(BaseModel):
    """Request to ingest a document: parse, chunk, and store it."""

    title: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    source_type: str = "user"
    language: str = "en"
    filename: str | None = None
    url: str | None = None


class DocumentMetadata(BaseModel):
    """Metadata for an ingested document."""

    document_id: str
    title: str
    source_type: str
    language: str
    filename: str | None = None
    url: str | None = None
    ingested_at: datetime
    chunk_count: int


class DocumentDetail(BaseModel):
    """A stored document together with its chunks."""

    document: DocumentMetadata
    chunks: list[Chunk]


class DocumentList(BaseModel):
    """A listing of ingested documents."""

    documents: list[DocumentMetadata]
    count: int


# --- Retrieval (slice 5) ---------------------------------------------------


class SearchRequest(BaseModel):
    """A similarity-search query over the indexed chunks."""

    query: str = Field(..., min_length=1)
    top_k: int | None = None


class RetrievedChunkResult(BaseModel):
    """A retrieved chunk with its similarity score and source metadata."""

    chunk_id: str
    document_id: str
    source_title: str
    source_type: str
    text: str
    score: float
    page_number: int | None = None


class SearchResponse(BaseModel):
    """Retrieval results plus the query and a count (retrieval metadata)."""

    query: str
    count: int
    results: list[RetrievedChunkResult]


# --- Embeddings (slice 3) --------------------------------------------------


class EmbeddingPreviewRequest(BaseModel):
    """Request to embed a short piece of text (debug/demo only)."""

    text: str = Field(..., min_length=1)


class EmbeddingPreviewResponse(BaseModel):
    """Embedding metadata plus a short preview of the vector."""

    model: str
    dimension: int
    preview: list[float]
