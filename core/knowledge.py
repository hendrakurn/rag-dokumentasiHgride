"""Knowledge service helpers for retrieval, context building, and ingest."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import CHUNK_OVERLAP, CHUNK_SIZE, SIMILARITY_TOP_K
from core.rag import get_vector_store


MAX_TOP_K = 20
DEFAULT_CONTEXT_MAX_CHARS = 6000


def _safe_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    if not metadata:
        return {}
    return json.loads(json.dumps(metadata, ensure_ascii=False, default=str))


def _source_from_metadata(metadata: dict[str, Any]) -> str:
    source = metadata.get("source") or metadata.get("url") or metadata.get("title")
    return str(source) if source else "Unknown"


def _score_to_float(score: Any) -> float | None:
    if score is None:
        return None
    try:
        return float(score)
    except (TypeError, ValueError):
        return None


def _normalize_top_k(top_k: int | None) -> int:
    requested = SIMILARITY_TOP_K if top_k is None else top_k
    return max(1, min(int(requested), MAX_TOP_K))


def search_knowledge(
    query: str,
    *,
    top_k: int | None = None,
    vector_store: Any | None = None,
) -> list[dict[str, Any]]:
    """Return raw Qdrant chunks for a query without calling an LLM."""
    query = query.strip()
    if not query:
        return []

    if vector_store is None:
        vector_store = get_vector_store()

    k = _normalize_top_k(top_k)
    search_with_score = getattr(vector_store, "similarity_search_with_score", None)

    if callable(search_with_score):
        try:
            pairs = search_with_score(query, k=k)
        except (AttributeError, NotImplementedError):
            pairs = None
        if pairs is not None:
            return [_document_result(document, score) for document, score in pairs]

    documents = vector_store.similarity_search(query, k=k)
    return [_document_result(document, None) for document in documents]


def _document_result(document: Any, score: Any) -> dict[str, Any]:
    metadata = _safe_metadata(getattr(document, "metadata", {}) or {})
    return {
        "content": str(getattr(document, "page_content", "")),
        "source": _source_from_metadata(metadata),
        "score": _score_to_float(score),
        "metadata": metadata,
    }


def build_context_payload(
    query: str,
    *,
    top_k: int | None = None,
    max_chars: int = DEFAULT_CONTEXT_MAX_CHARS,
    vector_store: Any | None = None,
) -> dict[str, Any]:
    """Build prompt-ready context from retrieved knowledge chunks."""
    results = search_knowledge(query, top_k=top_k, vector_store=vector_store)
    parts: list[str] = []
    sources: list[str] = []
    seen_sources: set[str] = set()

    for index, result in enumerate(results, 1):
        source = result["source"]
        if source and source != "Unknown" and source not in seen_sources:
            seen_sources.add(source)
            sources.append(source)

        parts.append(
            "\n".join(
                [
                    f"[{index}] Source: {source}",
                    result["content"].strip(),
                ]
            )
        )

    context = "\n\n---\n\n".join(parts).strip()
    if len(context) > max_chars:
        context = context[:max_chars].rstrip()

    return {
        "query": query,
        "context": context,
        "sources": sources,
        "chunks_used": len(results),
    }


def ingest_text_knowledge(
    *,
    title: str,
    content: str,
    source: str | None = None,
    metadata: dict[str, Any] | None = None,
    vector_store: Any | None = None,
) -> dict[str, Any]:
    """Add text knowledge to the existing Qdrant collection."""
    clean_title = title.strip()
    clean_content = content.strip()
    if not clean_title:
        raise ValueError("title is required.")
    if not clean_content:
        raise ValueError("content is required.")

    if vector_store is None:
        vector_store = get_vector_store()

    clean_source = source.strip() if isinstance(source, str) and source.strip() else clean_title
    document_metadata = _safe_metadata(metadata)
    document_metadata.update(
        {
            "title": clean_title,
            "source": clean_source,
            "knowledge_type": "manual_text",
        }
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    documents = splitter.split_documents(
        [Document(page_content=clean_content, metadata=document_metadata)]
    )
    vector_store.add_documents(documents)

    return {
        "message": "Knowledge ingested.",
        "source": clean_source,
        "chunks_added": len(documents),
    }
