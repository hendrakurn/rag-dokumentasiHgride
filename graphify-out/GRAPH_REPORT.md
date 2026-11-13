# Graph Report - dokProjekLangchain-1  (2026-08-29)

## Corpus Check
- 43 files · ~239,639 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 213 nodes · 265 edges · 64 communities (20 shown, 44 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- rag.py
- app_streamlit.py
- test_phase3_memory.py
- api.py
- get_vector_store
- Workflow
- Setup Graphify Dari Nol
- core/__init__.py
- HGrid247 Expert Skill
- HGrid247-3.5 DE
- Graphify Rules
- Graphify Workflow
- Q: Cek apakah fase 3 sudah dieksekusi dan bagaimana hasilnya
- Agent Context: HGrid API
- Design System
- Fase 1: Web Documentation
- Fase 2: Backend API Documentation
- Fase 3: Conversational Memory
- Glassmorphism Frontend Plan
- Implementation Plan
- Product Context
- Running Guide
- Setup Steps
- Dynamic Parameter
- Gemini 3.6 Flash
- UI screenshot showing a chat answer with source anchors and a preview chunk retrieval button
- UI screenshot of a multiline chat input field that has automatically grown in height
- UI screenshot of the chat interface on a desktop view showing source anchors and a long prompt
- UI screenshot of a focused chat input field with a single line prompt
- UI screenshot of a very long multiline chat input field showing autogrow behavior
- UI screenshot of the chat input field on mobile showing autogrow behavior
- UI screenshot of the chat interface on mobile showing source anchors and a long prompt
- UI screenshot showing the chat interface after an answer has been provided, with source anchors visible
- UI screenshot of a focused chat input field with a short prompt
- UI screenshot of a compact, fixed-width chat input field
- UI screenshot of the final desktop chat interface design
- UI screenshot of an empty, fixed-width chat input field
- UI screenshot of the final mobile chat interface design
- UI screenshot of a multiline chat input with a centered send button
- UI screenshot showing a user avatar row and a centered send button in the chat interface
- UI screenshot of the HGrid247 AI Assistant dashboard on desktop with a dark sidebar and configuration cards
- UI screenshot of the HGrid247 AI Assistant dashboard on mobile showing configuration cards and a 'Kirim' button
- UI screenshot of a focused chat interface on desktop with a light purple background
- UI screenshot of the final focused chat interface on mobile
- UI screenshot of a focused chat interface on mobile with a light purple background
- Final Glass Desktop UI
- Final Glass Mobile UI
- Desktop UI Screenshot
- Mobile UI Screenshot
- Playwright MCP Deployment State
- Qdrant
- hgrid_skill/__init__.py
- tools/__init__.py

## God Nodes (most connected - your core abstractions)
1. `tanya_hgrid_with_memory()` - 21 edges
2. `get_vector_store()` - 15 edges
3. `tanya_hgrid()` - 15 edges
4. `tanya_hgrid_with_memory_stream()` - 15 edges
5. `Setup Graphify Dari Nol` - 14 edges
6. `get_llm()` - 10 edges
7. `create_hgrid_agent()` - 8 edges
8. `FakeVectorStore` - 7 edges
9. `chat()` - 6 edges
10. `chat_with_memory()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `HGrid Chat Final UI` --references--> `HGrid247-3.5 DE`  [EXTRACTED]
  hgrid-chat-after-answer-final.png → hgrid-chat-after-answer-final-snapshot.md
- `startup()` --calls--> `get_llm()`  [EXTRACTED]
  api.py → core/rag.py
- `chat()` --calls--> `tanya_hgrid()`  [EXTRACTED]
  api.py → core/rag.py
- `chat_with_memory()` --calls--> `tanya_hgrid_with_memory()`  [EXTRACTED]
  api.py → core/rag.py
- `init_resources()` --calls--> `get_llm()`  [EXTRACTED]
  app_streamlit.py → core/rag.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Standard Data Pipeline Flow** — operator_source, operator_assembly, operator_sink [EXTRACTED 1.00]
- **HGrid AI Assistant Dashboard Layouts** — hgrid_colorize_desktop_png, hgrid_colorize_mobile_png, hgrid_focused_desktop_png, hgrid_focused_final_mobile_png, hgrid_focused_mobile_png [EXTRACTED 1.00]
- **HGrid Chat UI Evolution** — hgrid_chat_final_answer_png, hgrid_chat_final_autogrow_png, hgrid_chat_final_desktop_png, hgrid_chat_final_focused_fresh_png, hgrid_chat_final_long_autogrow_png, hgrid_chat_final_mobile_autogrow_png, hgrid_chat_final_mobile_png, hgrid_chat_final_post_answer_png, hgrid_chat_final_short_focus_png, hgrid_chat_monomorphism_compact_fixed_png, hgrid_chat_monomorphism_desktop_final_png, hgrid_chat_monomorphism_empty_fixed_png, hgrid_chat_monomorphism_mobile_final_png, hgrid_chat_send_centered_multiline_png, hgrid_chat_user_avatar_row_send_centered_png [EXTRACTED 1.00]
- **Workflow Execution Context** — engine, dynamic_parameter, workflow [INFERRED 0.80]

## Communities (64 total, 44 thin omitted)

### Community 0 - "rag.py"
Cohesion: 0.16
Nodes (26): AIMessage, Terminal chat for HGrid247 AI Assistant., Backward-compatible helper that returns only the answer text., tanya_hgrid(), ChatGoogleGenerativeAI, _build_chunk_previews(), _build_contextual_retrieval_query(), _clean_chat_history() (+18 more)

### Community 1 - "app_streamlit.py"
Cohesion: 0.13
Nodes (15): assistant_message_from_answer(), coerce_streamed_answer(), init_resources(), memory_history_from_messages(), Any, HGrid247 AI Assistant - Streamlit web interface., Initialize resources once per Streamlit process., render_chat_history() (+7 more)

### Community 2 - "test_phase3_memory.py"
Cohesion: 0.18
Nodes (7): Central configuration for HGrid247 AI Assistant., Document, RunnableLambda, ApiMemoryTests, fake_llm(), FakeVectorStore, RagMemoryTests

### Community 3 - "api.py"
Cohesion: 0.21
Nodes (15): chat(), chat_with_memory(), ChatMessage, ChatRequest, ChatResponse, ChatSessionRequest, health_check(), HealthResponse (+7 more)

### Community 4 - "get_vector_store"
Cohesion: 0.09
Nodes (27): Initialize reusable RAG resources when the API starts., startup(), Prompt templates for HGrid247 AI Assistant., get_embeddings(), get_vector_store(), Initialize the local embedding model., Connect to the existing Qdrant vector store., create_hgrid_agent() (+19 more)

### Community 5 - "Workflow"
Cohesion: 0.38
Nodes (7): Engine, HFS Source, Assembly Operator, Sink Operator, Source Operator, Troubleshooting, Workflow

### Community 6 - "Setup Graphify Dari Nol"
Cohesion: 0.09
Nodes (21): 10. Workflow Harian Yang Disarankan, 11. Status Graphify Di Project Ini, 12. Troubleshooting, 13. Command Ringkas, 1. Apa Itu Graphify, 2. Prasyarat, 3. Install Graphify, 4. Masuk Ke Folder Project (+13 more)

### Community 8 - "HGrid247 Expert Skill"
Cohesion: 0.33
Nodes (5): Cara Menggunakan, HGrid247 Expert Skill, Kemampuan, Pengetahuan Inti, Tools yang Tersedia

### Community 12 - "Q: Cek apakah fase 3 sudah dieksekusi dan bagaimana hasilnya"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Cek apakah fase 3 sudah dieksekusi dan bagaimana hasilnya, Source Nodes

## Knowledge Gaps
- **70 isolated node(s):** `1. Apa Itu Graphify`, `2. Prasyarat`, `Opsi A: Install Dengan pip di Virtualenv`, `Opsi B: Install Dengan uv`, `Opsi C: Install Dengan pipx` (+65 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_vector_store()` connect `get_vector_store` to `rag.py`, `app_streamlit.py`, `api.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `tanya_hgrid_with_memory()` connect `rag.py` to `test_phase3_memory.py`, `api.py`, `get_vector_store`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `tanya_hgrid()` connect `rag.py` to `api.py`, `get_vector_store`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **What connects `1. Apa Itu Graphify`, `2. Prasyarat`, `Opsi A: Install Dengan pip di Virtualenv` to the rest of the system?**
  _70 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app_streamlit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `get_vector_store` be split into smaller, more focused modules?**
  _Cohesion score 0.09462365591397849 - nodes in this community are weakly interconnected._
- **Should `Setup Graphify Dari Nol` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._