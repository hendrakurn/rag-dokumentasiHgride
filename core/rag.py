"""Reusable RAG engine for retrieval and answer generation."""

from __future__ import annotations

from typing import Any, Iterator

import qdrant_client
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

from core.config import (
    EMBEDDING_MODEL,
    GEMINI_MODEL,
    MAX_HISTORY_MESSAGES,
    QDRANT_COLLECTION,
    QDRANT_URL,
    SIMILARITY_TOP_K,
)
from core.prompts import RAG_PROMPT_SIMPLE, RAG_PROMPT_WITH_MEMORY


def get_embeddings() -> HuggingFaceEmbeddings:
    """Initialize the local embedding model."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def get_vector_store(embeddings: HuggingFaceEmbeddings | None = None) -> QdrantVectorStore:
    """Connect to the existing Qdrant vector store."""
    if embeddings is None:
        embeddings = get_embeddings()

    client = qdrant_client.QdrantClient(url=QDRANT_URL)
    return QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embedding=embeddings,
    )


def get_llm() -> ChatGoogleGenerativeAI:
    """Initialize Gemini for answer generation."""
    return ChatGoogleGenerativeAI(model=GEMINI_MODEL)


def extract_text_from_response(response: Any) -> str:
    """Extract plain text from Gemini responses across SDK formats."""
    content = getattr(response, "content", response)

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                text = block.get("text") or block.get("content")
                if text:
                    parts.append(str(text))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts).strip()

    return str(content).strip()


def extract_text_chunk_from_response(response: Any) -> str:
    """Extract streamed text without trimming token boundary whitespace."""
    content = getattr(response, "content", response)

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                text = block.get("text") or block.get("content")
                if text is not None:
                    parts.append(str(text))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)

    return str(content)


def _collect_sources(documents: list[Any]) -> list[str]:
    sources: list[str] = []
    seen: set[str] = set()

    for doc in documents:
        source = doc.metadata.get("source") if getattr(doc, "metadata", None) else None
        if source and source not in seen:
            seen.add(source)
            sources.append(source)

    return sources


def _build_chunk_previews(documents: list[Any]) -> list[dict[str, str]]:
    previews: list[dict[str, str]] = []

    for doc in documents:
        source = doc.metadata.get("source", "Unknown") if getattr(doc, "metadata", None) else "Unknown"
        text = " ".join(getattr(doc, "page_content", "").split())
        previews.append(
            {
                "source": source,
                "preview": text[:260] + ("..." if len(text) > 260 else ""),
            }
        )

    return previews


def _empty_question_result() -> dict[str, Any]:
    return {
        "jawaban": "Tuliskan pertanyaan tentang HGrid247 terlebih dahulu.",
        "sumber": [],
        "chunks_used": 0,
        "retrieved_chunks": [],
    }


def _clean_chat_history(chat_history: Any) -> list[dict[str, str]]:
    if not isinstance(chat_history, list):
        return []

    cleaned: list[dict[str, str]] = []
    for message in chat_history:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        raw_content = message.get("content", "")
        if raw_content is None:
            continue

        content = str(raw_content).strip()

        if role not in {"user", "assistant"} or not content:
            continue

        cleaned.append({"role": role, "content": content})

    return cleaned[-MAX_HISTORY_MESSAGES:]


def _to_langchain_messages(chat_history: list[dict[str, str]]) -> list[HumanMessage | AIMessage]:
    messages: list[HumanMessage | AIMessage] = []

    for message in chat_history:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            messages.append(AIMessage(content=message["content"]))

    return messages


def _build_contextual_retrieval_query(pertanyaan: str, chat_history: list[dict[str, str]]) -> str:
    if not chat_history:
        return pertanyaan

    history_lines = []
    for message in chat_history:
        speaker = "User" if message["role"] == "user" else "Assistant"
        history_lines.append(f"{speaker}: {message['content']}")

    return "\n".join(
        [
            "Konteks percakapan sebelumnya:",
            "\n".join(history_lines),
            "",
            f"Pertanyaan sekarang: {pertanyaan}",
        ]
    )


def tanya_hgrid(
    pertanyaan: str,
    vector_store: QdrantVectorStore | None = None,
    llm: ChatGoogleGenerativeAI | None = None,
) -> dict[str, Any]:
    """
    Run the HGrid247 RAG flow.

    Returns a dictionary with:
    - jawaban: answer text
    - sumber: unique source URLs used by retrieval
    - chunks_used: number of chunks retrieved
    - retrieved_chunks: short previews for UI inspection
    """
    pertanyaan = pertanyaan.strip()
    if not pertanyaan:
        return _empty_question_result()

    if vector_store is None:
        vector_store = get_vector_store()
    if llm is None:
        llm = get_llm()

    hasil_pencarian = vector_store.similarity_search(pertanyaan, k=SIMILARITY_TOP_K)
    konteks = "\n\n---\n\n".join(doc.page_content for doc in hasil_pencarian)

    prompt = PromptTemplate.from_template(RAG_PROMPT_SIMPLE)
    chain = prompt | llm
    jawaban_raw = chain.invoke({"konteks": konteks, "pertanyaan": pertanyaan})

    return {
        "jawaban": extract_text_from_response(jawaban_raw),
        "sumber": _collect_sources(hasil_pencarian),
        "chunks_used": len(hasil_pencarian),
        "retrieved_chunks": _build_chunk_previews(hasil_pencarian),
    }


def tanya_hgrid_with_memory(
    pertanyaan: str,
    chat_history: list[dict[str, Any]] | None,
    vector_store: QdrantVectorStore | None = None,
    llm: ChatGoogleGenerativeAI | None = None,
) -> dict[str, Any]:
    """
    Run the HGrid247 RAG flow with limited conversational memory.

    chat_history only uses the latest MAX_HISTORY_MESSAGES valid messages.
    The contextual query is used for retrieval, while the original question is
    preserved for answer generation.
    """
    pertanyaan = pertanyaan.strip()
    if not pertanyaan:
        return _empty_question_result()

    cleaned_history = _clean_chat_history(chat_history)
    lc_history = _to_langchain_messages(cleaned_history)
    retrieval_query = _build_contextual_retrieval_query(pertanyaan, cleaned_history)

    if vector_store is None:
        vector_store = get_vector_store()
    if llm is None:
        llm = get_llm()

    hasil_pencarian = vector_store.similarity_search(retrieval_query, k=SIMILARITY_TOP_K)
    konteks = "\n\n---\n\n".join(doc.page_content for doc in hasil_pencarian)

    chain = RAG_PROMPT_WITH_MEMORY | llm
    jawaban_raw = chain.invoke(
        {
            "konteks": konteks,
            "chat_history": lc_history,
            "pertanyaan": pertanyaan,
        }
    )

    return {
        "jawaban": extract_text_from_response(jawaban_raw),
        "sumber": _collect_sources(hasil_pencarian),
        "chunks_used": len(hasil_pencarian),
        "retrieved_chunks": _build_chunk_previews(hasil_pencarian),
    }

def tanya_hgrid_with_memory_stream(
    pertanyaan: str,
    chat_history: list[dict[str, Any]] | None,
    vector_store: QdrantVectorStore | None = None,
    llm: ChatGoogleGenerativeAI | None = None,
) -> tuple[Iterator[str], dict[str, Any]]:
    """Run the HGrid247 RAG flow and stream answer text chunks."""
    pertanyaan = pertanyaan.strip()
    if not pertanyaan:
        empty = _empty_question_result()
        return iter([empty["jawaban"]]), {
            "sumber": empty["sumber"],
            "chunks_used": empty["chunks_used"],
            "retrieved_chunks": empty["retrieved_chunks"],
        }

    cleaned_history = _clean_chat_history(chat_history)
    lc_history = _to_langchain_messages(cleaned_history)
    retrieval_query = _build_contextual_retrieval_query(pertanyaan, cleaned_history)

    if vector_store is None:
        vector_store = get_vector_store()
    if llm is None:
        llm = get_llm()

    hasil_pencarian = vector_store.similarity_search(retrieval_query, k=SIMILARITY_TOP_K)
    konteks = "\n\n---\n\n".join(doc.page_content for doc in hasil_pencarian)

    chain = RAG_PROMPT_WITH_MEMORY | llm
    raw_stream = chain.stream(
        {
            "konteks": konteks,
            "chat_history": lc_history,
            "pertanyaan": pertanyaan,
        }
    )

    def text_stream() -> Iterator[str]:
        for chunk in raw_stream:
            text = extract_text_chunk_from_response(chunk)
            if text:
                yield text

    return text_stream(), {
        "sumber": _collect_sources(hasil_pencarian),
        "chunks_used": len(hasil_pencarian),
        "retrieved_chunks": _build_chunk_previews(hasil_pencarian),
    }

