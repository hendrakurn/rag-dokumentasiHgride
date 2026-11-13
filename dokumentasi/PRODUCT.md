# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Existing Python 3.12 RAG project with LangChain, Qdrant, HuggingFace embeddings, Gemini, and a terminal chat loop. Phase 1 adds Streamlit as the web interface.

## Users

Primary users are technical HGrid247 users and Solusi247 team members who need fast, documentation-grounded answers while learning, operating, or troubleshooting HGrid247-3.5 DE.

## Product Purpose

HGrid247 AI Assistant answers questions about the HGrid247-3.5 DE documentation through retrieval-augmented generation. Success means users can ask natural-language questions in Indonesian and receive clear answers with traceable documentation sources.

## Positioning

The product is grounded in the HGrid247 documentation collection stored in Qdrant rather than acting as a generic chatbot.

## Operating Context

The current system ingests 26 HGrid247 documentation pages into the `hgrid247_docs` Qdrant collection, then retrieves relevant chunks and sends them to Gemini for answer generation. Phase 1 moves the interaction from terminal-only chat into a Streamlit browser UI.

## Capabilities and Constraints

Confirmed capabilities: document ingestion, vector search, Gemini generation, Indonesian technical answers, source URLs, and a planned Streamlit chat surface. Constraints: keep the collection name `hgrid247_docs`, do not change `ingest.py` unless explicitly requested, use `core/config.py` for configuration, and handle Gemini response content as either text or list blocks.

Open decisions: production deployment target, authentication, logging, analytics, and enterprise branding assets are not confirmed yet.

## Brand Commitments

Use the product name `HGrid247 AI Assistant` and preserve the Solusi247/HGrid247 technical product context. No official visual identity assets were found in the repository.

## Evidence on Hand

Implementation plan: `implemetation.md`. Existing terminal RAG: `chat.py`. Existing ingestion script: `ingest.py`. Setup notes: `step.md`. The `.env` file exists, but its secret values were not read.

## Product Principles

1. Ground answers in retrieved HGrid247 documentation.
2. Keep the interface task-focused for repeated technical use.
3. Make sources visible so answers can be verified.
4. Keep shared RAG logic reusable across Streamlit, FastAPI, and later agent phases.
5. Avoid destructive or workflow-changing behavior unless a later phase explicitly adds it.
