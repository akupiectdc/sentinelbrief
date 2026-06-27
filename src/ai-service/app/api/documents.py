"""Document endpoints.

* ``POST /documents/chunk`` - chunking preview (no storage).
* ``POST /documents``       - ingest a document: parse, chunk, and store it.
* ``GET  /documents``       - list ingested documents.
* ``GET  /documents/{id}``  - fetch a stored document with its chunks.

Embeddings and Qdrant-backed vector storage are added in later slices; this
store keeps documents in memory.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import embedding_provider_dependency, vector_store_dependency
from app.core.config import Settings, get_settings
from app.documents.chunking import chunk_text
from app.documents.parsing import parse_text
from app.documents.store import InMemoryDocumentStore, get_document_store
from app.models import (
    ChunkRequest,
    ChunkResponse,
    DocumentDetail,
    DocumentList,
    DocumentMetadata,
    IngestRequest,
)
from app.providers.base import EmbeddingProvider
from app.vectorstores.qdrant import QdrantVectorStore

router = APIRouter(prefix="/documents", tags=["documents"])

# Stable namespace so the same source (filename, url, or title) always maps to
# the same document_id. This makes re-ingestion idempotent: a document updates
# in place instead of accumulating duplicate copies on every reseed.
_DOCUMENT_NAMESPACE = uuid.UUID("9f1a7b30-5e2c-4c8a-9b6d-2c5a1e8f4d33")


def _document_id(request: IngestRequest) -> str:
    """Derive a deterministic document_id from the document's source identity."""
    source_key = request.filename or request.url or request.title
    return str(uuid.uuid5(_DOCUMENT_NAMESPACE, source_key))


@router.post("/chunk", response_model=ChunkResponse)
def chunk_document(
    request: ChunkRequest,
    settings: Settings = Depends(get_settings),
) -> ChunkResponse:
    """Parse and chunk a document's text, returning chunks with metadata."""
    document_id = str(uuid.uuid4())
    text = parse_text(request.text)
    chunks = chunk_text(
        text,
        document_id=document_id,
        source_title=request.title,
        source_type=request.source_type,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return ChunkResponse(
        document_id=document_id,
        title=request.title,
        chunk_count=len(chunks),
        chunks=chunks,
    )


@router.post("", response_model=DocumentMetadata, status_code=201)
async def ingest_document(
    request: IngestRequest,
    settings: Settings = Depends(get_settings),
    store: InMemoryDocumentStore = Depends(get_document_store),
    embedder: EmbeddingProvider = Depends(embedding_provider_dependency),
    vector_store: QdrantVectorStore = Depends(vector_store_dependency),
) -> DocumentMetadata:
    """Parse and chunk a document, embed its chunks, and store both.

    Chunk text and metadata are kept in the document store; the embedding
    vectors are persisted in Qdrant for similarity search.
    """
    document_id = _document_id(request)
    text = parse_text(request.text)
    chunks = chunk_text(
        text,
        document_id=document_id,
        source_title=request.title,
        source_type=request.source_type,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    # Replace any previous version of this document so re-ingesting updates it
    # in place rather than leaving duplicate vectors behind.
    await vector_store.delete_document(document_id)
    if chunks:
        vectors = await embedder.embed([chunk.text for chunk in chunks])
        await vector_store.upsert(chunks, vectors)
    metadata = DocumentMetadata(
        document_id=document_id,
        title=request.title,
        source_type=request.source_type,
        language=request.language,
        filename=request.filename,
        url=request.url,
        ingested_at=datetime.now(UTC),
        chunk_count=len(chunks),
    )
    store.add(metadata, chunks)
    return metadata


@router.get("", response_model=DocumentList)
def list_documents(
    store: InMemoryDocumentStore = Depends(get_document_store),
) -> DocumentList:
    """List the metadata of all ingested documents."""
    documents = [stored.metadata for stored in store.list()]
    return DocumentList(documents=documents, count=len(documents))


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: str,
    store: InMemoryDocumentStore = Depends(get_document_store),
) -> DocumentDetail:
    """Return a stored document with its chunks, or 404 if unknown."""
    stored = store.get(document_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetail(document=stored.metadata, chunks=stored.chunks)
