# Implementation Plan: HGrid247 AI Assistant

> Rencana pengembangan lengkap untuk mengubah asisten Q&A terminal menjadi AI Agent yang cerdas, memiliki antarmuka web, API backend, conversational memory, dan kemampuan melakukan aksi langsung pada ekosistem HGrid247.

---

## Status Proyek Saat Ini (Baseline)

### Arsitektur yang Sudah Berjalan

```
┌─────────────────────┐     ┌──────────────────┐     ┌──────────────┐
│   ingest.py         │     │    chat.py        │     │   Qdrant     │
│                     │     │                   │     │  (Docker)    │
│ 1. Scrape 26 URL    │────▶│ 1. Koneksi Qdrant │◀───▶│ localhost    │
│ 2. Chunk (700 char) │     │ 2. Similarity     │     │ :6333        │
│ 3. Embed (MiniLM)   │     │    Search (k=3)   │     │              │
│ 4. Store ke Qdrant  │     │ 3. Prompt+Gemini  │     │ Collection:  │
│                     │     │ 4. Terminal Loop   │     │ hgrid247_docs│
└─────────────────────┘     └──────────────────┘     └──────────────┘
```

### File yang Sudah Ada

| File | Fungsi | Status |
|------|--------|--------|
| `ingest.py` | Scrape 26 halaman dokumentasi HGrid247, chunking, embedding, simpan ke Qdrant | ✅ Berjalan |
| `chat.py` | RAG Q&A di terminal: similarity search → prompt → Gemini 3.6 Flash | ✅ Berjalan |
| `.env` | Menyimpan `GOOGLE_API_KEY` | ✅ Ada |
| `venv/` | Python 3.12 virtual environment | ✅ Ada |

### Dependencies yang Sudah Terinstal

```
langchain-core==1.6.0
langchain-community==0.4.2           # WARNING: deprecated, akan di-sunset
langchain-google-genai==4.3.5
langchain-huggingface==1.2.2
langchain-qdrant==1.1.0
langchain-text-splitters==1.1.2
qdrant-client==1.19.0
google-genai==2.20.0
huggingface_hub==1.28.0
python-dotenv==1.2.3
```

### Konfigurasi Infrastruktur

- **Qdrant**: Docker container `qdrant/qdrant` di `localhost:6333` dengan volume `qdrant_storage`
- **Embedding Model**: `all-MiniLM-L6-v2` (HuggingFace, local, gratis)
- **LLM**: `gemini-3.6-flash` via Google API
- **Collection Name**: `hgrid247_docs` (260 chunks)

### Domain Knowledge: HGrid247-3.5 DE

HGrid247-3.5 DE adalah **multi-platform, drag-and-drop big data engineering ETL tool** untuk batch dan stream processing milik Solusi247. Key concepts:

- **Workflow**: `Source → Assembly → Sink`
- **Operators**: Source (baca data), Assembly (transformasi), Sink (simpan data)
- **Build Targets**: MapReduce, Spark RDD, Spark Dataset, Beam (Batch/Streaming), Flink (Batch/Streaming), Tez, PySpark
- **Dokumentasi**: 26 halaman HTML di `hgridde.labs247.id`

---

## Target Struktur Proyek Akhir

```
dokProjekLangchain-1/
├── .env                          # API keys (GOOGLE_API_KEY)
├── implemetation.md              # Dokumen ini
├── requirements.txt              # [NEW] Semua dependencies
│
├── core/                         # [NEW] Shared logic (used by semua fase)
│   ├── __init__.py
│   ├── config.py                 # Konfigurasi (env vars, constants)
│   ├── rag.py                    # RAG engine (embedding, retrieval, generate)
│   └── prompts.py                # Semua prompt templates
│
├── ingest.py                     # [EXISTING] Data ingestion script
├── chat.py                       # [EXISTING] Terminal chatbot
│
├── app_streamlit.py              # [NEW] Fase 1: Streamlit Web UI
├── api.py                        # [NEW] Fase 2: FastAPI backend
│
├── hgrid_skill/                  # [NEW] Fase 4: AI Agent Skill Package
│   ├── __init__.py
│   ├── SKILL.md                  # Skill instruction file
│   ├── tools/                    # Agent action tools
│   │   ├── __init__.py
│   │   ├── hgrid_api.py          # API interactions with HGrid247
│   │   ├── script_runner.py      # Execute HGrid scripts
│   │   └── workflow_builder.py   # Build workflows via API
│   └── agent.py                  # Agent orchestrator
│
└── venv/                         # Python virtual environment
```

---

## FASE 1: Web Interface dengan Streamlit

**Status:** Selesai pada 2026-08-26. Implementasi mencakup `core/` package, refactor `chat.py`, `app_streamlit.py`, instalasi Streamlit di `venv/`, dan `requirements.txt` untuk dependency Fase 1.

### Tujuan
Mengubah interaksi terminal (`chat.py`) menjadi web UI interaktif yang bisa diakses di browser, dengan tampilan chat bubble modern.

### Prasyarat
```bash
# Install Streamlit
source venv/bin/activate
pip install streamlit
```

### File yang Dibuat/Dimodifikasi

---

#### [NEW] `core/__init__.py`
File kosong untuk menjadikan `core/` sebagai Python package.

```python
# core/__init__.py
```

---

#### [NEW] `core/config.py`
Konfigurasi terpusat. Semua file lain import dari sini.

```python
"""Konfigurasi terpusat untuk HGrid247 AI Assistant."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Qdrant ---
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "hgrid247_docs")

# --- Embedding ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --- LLM ---
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- RAG ---
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
```

---

#### [NEW] `core/prompts.py`
Semua prompt template di satu tempat.

```python
"""Prompt templates untuk HGrid247 AI Assistant."""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Prompt untuk RAG tanpa memory (Fase 1)
RAG_PROMPT_SIMPLE = """
Kamu adalah asisten teknis AI untuk platform HGrid247-3.5 DE milik Solusi247.
Gunakan HANYA konteks dokumentasi di bawah ini untuk menjawab pertanyaan user.
Jawab dalam Bahasa Indonesia yang jelas dan terstruktur.
Jika kamu tidak menemukan jawabannya di dalam konteks, katakan dengan sopan
bahwa informasi tersebut belum tersedia di dokumentasi.

Konteks Dokumentasi:
{konteks}

Pertanyaan User: {pertanyaan}

Jawaban:
"""

# Prompt untuk RAG dengan memory (Fase 3) - akan digunakan nanti
RAG_PROMPT_WITH_MEMORY = ChatPromptTemplate.from_messages([
    ("system", """Kamu adalah asisten teknis AI untuk platform HGrid247-3.5 DE milik Solusi247.
Gunakan HANYA konteks dokumentasi di bawah ini untuk menjawab pertanyaan user.
Jawab dalam Bahasa Indonesia yang jelas dan terstruktur.
Jika kamu tidak menemukan jawabannya di dalam konteks, katakan dengan sopan
bahwa informasi tersebut belum tersedia di dokumentasi.

Konteks Dokumentasi:
{konteks}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{pertanyaan}"),
])

# Prompt untuk Agent (Fase 4) - akan digunakan nanti
AGENT_SYSTEM_PROMPT = """Kamu adalah HGrid247 AI Agent - agen cerdas yang menguasai
platform HGrid247-3.5 DE secara penuh. Kamu memiliki kemampuan:

1. MENJAWAB pertanyaan tentang HGrid247 berdasarkan dokumentasi
2. MEMBUAT workflow HGrid baru (Source → Assembly → Sink)
3. MENJALANKAN script di HGrid247
4. MENGELOLA project, package, dan workflow
5. TROUBLESHOOTING masalah pada pipeline data

Gunakan tools yang tersedia untuk membantu user. Selalu konfirmasi sebelum
melakukan aksi yang bersifat destruktif (hapus, overwrite).

Konteks Dokumentasi:
{konteks}
"""
```

---

#### [NEW] `core/rag.py`
Engine RAG yang bisa di-reuse oleh Streamlit, FastAPI, dan Agent.

```python
"""RAG Engine - shared logic untuk retrieval dan generation."""
import qdrant_client
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import PromptTemplate

from core.config import (
    QDRANT_URL, QDRANT_COLLECTION, EMBEDDING_MODEL,
    GEMINI_MODEL, SIMILARITY_TOP_K
)
from core.prompts import RAG_PROMPT_SIMPLE


def get_embeddings():
    """Inisialisasi embedding model (singleton-friendly)."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def get_vector_store(embeddings=None):
    """Koneksi ke Qdrant vector store."""
    if embeddings is None:
        embeddings = get_embeddings()
    client = qdrant_client.QdrantClient(url=QDRANT_URL)
    return QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embedding=embeddings,
    )


def get_llm():
    """Inisialisasi Gemini LLM."""
    return ChatGoogleGenerativeAI(model=GEMINI_MODEL)


def extract_text_from_response(response):
    """Extract plain text dari response Gemini (handle list-of-dicts format)."""
    if isinstance(response.content, list):
        return "\n".join(
            block["text"] for block in response.content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return response.content


def tanya_hgrid(pertanyaan: str, vector_store=None, llm=None) -> dict:
    """
    Fungsi utama RAG: cari dokumen relevan, tanyakan ke LLM.
    
    Returns:
        dict dengan keys:
        - jawaban (str): Teks jawaban dari AI
        - sumber (list[str]): URL sumber dokumen yang digunakan
        - chunks_used (int): Jumlah chunks yang digunakan
    """
    if vector_store is None:
        vector_store = get_vector_store()
    if llm is None:
        llm = get_llm()

    # Retrieval: cari dokumen relevan
    hasil_pencarian = vector_store.similarity_search(pertanyaan, k=SIMILARITY_TOP_K)
    konteks = "\n\n---\n\n".join([doc.page_content for doc in hasil_pencarian])
    
    # Kumpulkan sumber URL unik
    sumber = list(set(
        doc.metadata.get("source", "Unknown")
        for doc in hasil_pencarian
        if doc.metadata.get("source")
    ))

    # Generation: tanyakan ke LLM
    prompt = PromptTemplate.from_template(RAG_PROMPT_SIMPLE)
    chain = prompt | llm
    jawaban_raw = chain.invoke({"konteks": konteks, "pertanyaan": pertanyaan})

    return {
        "jawaban": extract_text_from_response(jawaban_raw),
        "sumber": sumber,
        "chunks_used": len(hasil_pencarian),
    }
```

---

#### [NEW] `app_streamlit.py`
Aplikasi web Streamlit dengan chat interface.

```python
"""HGrid247 AI Assistant - Streamlit Web Interface."""
import streamlit as st
from core.rag import get_vector_store, get_llm, tanya_hgrid

# --- Page Config ---
st.set_page_config(
    page_title="HGrid247 AI Assistant",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 HGrid247 AI Assistant")
st.caption("Asisten teknis AI untuk platform HGrid247-3.5 DE milik Solusi247")

# --- Initialize (cache supaya tidak reload tiap interaksi) ---
@st.cache_resource
def init_resources():
    vector_store = get_vector_store()
    llm = get_llm()
    return vector_store, llm

vector_store, llm = init_resources()

# --- Session State untuk Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Tampilkan riwayat chat ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sumber"):
            with st.expander("📄 Sumber Dokumentasi"):
                for src in message["sumber"]:
                    st.markdown(f"- [{src}]({src})")

# --- Input dan Response ---
if prompt := st.chat_input("Tanya tentang HGrid247..."):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate jawaban
    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari jawaban..."):
            hasil = tanya_hgrid(prompt, vector_store=vector_store, llm=llm)
        
        st.markdown(hasil["jawaban"])
        
        if hasil["sumber"]:
            with st.expander("📄 Sumber Dokumentasi"):
                for src in hasil["sumber"]:
                    st.markdown(f"- [{src}]({src})")

    # Simpan ke session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": hasil["jawaban"],
        "sumber": hasil["sumber"],
    })
```

### Cara Menjalankan Fase 1

```bash
source venv/bin/activate
pip install streamlit

# Pastikan Qdrant running
docker start qdrant

# Jalankan Streamlit
streamlit run app_streamlit.py --server.port 8501
```

### Verifikasi Fase 1

1. Buka browser `http://localhost:8501`
2. Ketik pertanyaan: "Apa itu HGrid247?"
3. Pastikan jawaban muncul dalam format chat bubble
4. Pastikan sumber dokumentasi muncul di expander
5. Tanya beberapa pertanyaan berturut-turut, pastikan riwayat chat tampil

---

## FASE 2: Backend API (FastAPI)

### Tujuan
Memisahkan logika RAG menjadi REST API server sehingga bisa dikonsumsi oleh frontend apapun (React, mobile app, portal internal Solusi247, dll).

### Prasyarat
```bash
source venv/bin/activate
pip install fastapi uvicorn
```

### File yang Dibuat/Dimodifikasi

---

#### [NEW] `api.py`
FastAPI server dengan endpoint chat.

```python
"""HGrid247 AI Assistant - FastAPI Backend."""
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.rag import get_vector_store, get_llm, tanya_hgrid

# --- App ---
app = FastAPI(
    title="HGrid247 AI Assistant API",
    description="REST API untuk asisten teknis AI HGrid247-3.5 DE",
    version="1.0.0",
)

# CORS (agar bisa diakses dari frontend yang berbeda domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk production, ganti dengan domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inisialisasi Resources saat startup ---
vector_store = None
llm = None

@app.on_event("startup")
async def startup():
    global vector_store, llm
    vector_store = get_vector_store()
    llm = get_llm()

# --- Models ---
class ChatRequest(BaseModel):
    pertanyaan: str = Field(..., min_length=1, description="Pertanyaan user tentang HGrid247")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID sesi chat")

class ChatResponse(BaseModel):
    jawaban: str
    sumber: list[str]
    chunks_used: int
    session_id: str

class HealthResponse(BaseModel):
    status: str
    qdrant: str
    collection: str
    model: str

# --- Endpoints ---
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Cek status kesehatan sistem."""
    from core.config import QDRANT_COLLECTION, GEMINI_MODEL
    return HealthResponse(
        status="healthy",
        qdrant="connected",
        collection=QDRANT_COLLECTION,
        model=GEMINI_MODEL,
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint utama tanya-jawab RAG.
    
    Menerima pertanyaan user, melakukan similarity search di Qdrant,
    lalu menghasilkan jawaban menggunakan Gemini LLM.
    """
    try:
        hasil = tanya_hgrid(
            request.pertanyaan,
            vector_store=vector_store,
            llm=llm,
        )
        return ChatResponse(
            jawaban=hasil["jawaban"],
            sumber=hasil["sumber"],
            chunks_used=hasil["chunks_used"],
            session_id=request.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### Cara Menjalankan Fase 2

```bash
source venv/bin/activate
pip install fastapi uvicorn

# Pastikan Qdrant running
docker start qdrant

# Jalankan FastAPI server
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Verifikasi Fase 2

1. Buka Swagger UI: `http://localhost:8000/docs`
2. Test endpoint `GET /health` — cek koneksi Qdrant
3. Test endpoint `POST /api/chat` dengan body:
   ```json
   {"pertanyaan": "Apa itu HGrid247?"}
   ```
4. Pastikan response JSON berisi `jawaban`, `sumber`, dan `chunks_used`
5. Test dengan `curl`:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"pertanyaan": "Bagaimana cara membuat workflow?"}'
   ```

---

## FASE 3: Conversational Memory (Context Awareness)

**Status:** Selesai pada 2026-08-27. Implementasi mencakup `MAX_HISTORY_MESSAGES`, fungsi `tanya_hgrid_with_memory()` di `core/rag.py`, integrasi memory di Streamlit, endpoint `POST /api/chat/session`, dan test fase 3.

### Tujuan
Membuat asisten bisa mengingat konteks percakapan sebelumnya dalam satu sesi. Contoh:
- User: "Apa itu Source di HGrid247?" → AI jawab
- User: "Lalu bagaimana cara membuatnya?" → AI tahu "membuatnya" = membuat Source

### Prasyarat
Tidak ada dependency baru. LangChain Core sudah mendukung message history.

### File yang Dibuat/Dimodifikasi

---

#### [MODIFY] `core/rag.py`
Tambahkan fungsi RAG baru yang mendukung chat history.

```python
# Tambahkan di core/rag.py (setelah fungsi tanya_hgrid yang sudah ada)

from langchain_core.messages import HumanMessage, AIMessage
from core.prompts import RAG_PROMPT_WITH_MEMORY


def tanya_hgrid_with_memory(
    pertanyaan: str,
    chat_history: list[dict],  # [{"role": "user"|"assistant", "content": "..."}]
    vector_store=None,
    llm=None,
) -> dict:
    """
    RAG dengan conversational memory.
    
    Args:
        pertanyaan: Pertanyaan user saat ini
        chat_history: Riwayat percakapan sebelumnya
        vector_store: Qdrant vector store instance
        llm: Gemini LLM instance
    
    Returns:
        dict: jawaban, sumber, chunks_used
    """
    if vector_store is None:
        vector_store = get_vector_store()
    if llm is None:
        llm = get_llm()

    # Konversi chat_history ke LangChain message objects
    lc_history = []
    for msg in chat_history:
        if msg["role"] == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_history.append(AIMessage(content=msg["content"]))

    # Retrieval
    hasil_pencarian = vector_store.similarity_search(pertanyaan, k=SIMILARITY_TOP_K)
    konteks = "\n\n---\n\n".join([doc.page_content for doc in hasil_pencarian])
    sumber = list(set(
        doc.metadata.get("source", "Unknown")
        for doc in hasil_pencarian
        if doc.metadata.get("source")
    ))

    # Generation dengan history
    chain = RAG_PROMPT_WITH_MEMORY | llm
    jawaban_raw = chain.invoke({
        "konteks": konteks,
        "chat_history": lc_history,
        "pertanyaan": pertanyaan,
    })

    return {
        "jawaban": extract_text_from_response(jawaban_raw),
        "sumber": sumber,
        "chunks_used": len(hasil_pencarian),
    }
```

---

#### [MODIFY] `app_streamlit.py`
Update Streamlit untuk menggunakan `tanya_hgrid_with_memory`.

**Perubahan utama**: Ganti pemanggilan `tanya_hgrid()` menjadi `tanya_hgrid_with_memory()` dengan menyertakan `st.session_state.messages` sebagai chat history.

```python
# Di bagian generate jawaban, ganti:
#   hasil = tanya_hgrid(prompt, vector_store=vector_store, llm=llm)
# menjadi:

from core.rag import tanya_hgrid_with_memory

# Siapkan history (tanpa sumber, hanya role dan content)
history = [
    {"role": m["role"], "content": m["content"]}
    for m in st.session_state.messages
]

hasil = tanya_hgrid_with_memory(
    prompt,
    chat_history=history,
    vector_store=vector_store,
    llm=llm,
)
```

---

#### [MODIFY] `api.py`
Tambahkan endpoint `/api/chat/session` yang menerima chat history.

```python
# Tambahkan model dan endpoint baru di api.py

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str

class ChatSessionRequest(BaseModel):
    pertanyaan: str = Field(..., min_length=1)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chat_history: list[ChatMessage] = Field(default_factory=list)

@app.post("/api/chat/session", response_model=ChatResponse)
async def chat_with_memory(request: ChatSessionRequest):
    """
    Endpoint tanya-jawab RAG dengan conversational memory.
    Kirimkan chat_history berisi riwayat percakapan untuk konteks.
    """
    from core.rag import tanya_hgrid_with_memory
    
    try:
        history = [{"role": m.role, "content": m.content} for m in request.chat_history]
        hasil = tanya_hgrid_with_memory(
            request.pertanyaan,
            chat_history=history,
            vector_store=vector_store,
            llm=llm,
        )
        return ChatResponse(
            jawaban=hasil["jawaban"],
            sumber=hasil["sumber"],
            chunks_used=hasil["chunks_used"],
            session_id=request.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

### Verifikasi Fase 3

1. **Streamlit**: Tanya "Apa itu Source di HGrid247?", lalu tanya "Bagaimana cara membuatnya?". AI harus paham "nya" = Source.
2. **API**: Kirim POST ke `/api/chat/session` dengan `chat_history` berisi percakapan sebelumnya:
   ```json
   {
     "pertanyaan": "Lalu bagaimana cara membuatnya?",
     "chat_history": [
       {"role": "user", "content": "Apa itu Source di HGrid247?"},
       {"role": "assistant", "content": "Source adalah operator awal..."}
     ]
   }
   ```

---

## FASE 4: HGrid AI Skill & Action Agent

### Tujuan
Mengubah sistem dari "asisten penjawab" menjadi **AI Agent** yang:
1. **Menguasai** semua dokumentasi HGrid247 secara penuh
2. **Bisa dipasang (install)** sebagai skill di AI coding assistant (Antigravity, Claude, Codex, dll)
3. **Mampu melakukan aksi** — bukan hanya menjawab, tapi langsung mengeksekusi perintah (menjalankan script, membuat workflow, troubleshooting)

### Konsep Arsitektur Agent

```
┌──────────────────────────────────────────────────────────┐
│                    HGrid247 AI Agent                     │
│                                                          │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────┐ │
│  │ RAG      │   │  LLM +       │   │    Tools         │ │
│  │ (Qdrant) │──▶│  Tool Calling │──▶│                  │ │
│  │          │   │  (Gemini)     │   │ 1. search_docs   │ │
│  └──────────┘   └──────────────┘   │ 2. run_script    │ │
│                                     │ 3. create_wf     │ │
│                                     │ 4. list_projects │ │
│                                     │ 5. troubleshoot  │ │
│                                     │ 6. shell_execute │ │
│                                     └──────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### File yang Dibuat

---

#### [NEW] `hgrid_skill/SKILL.md`
Skill instruction file. Ini adalah file yang akan dibaca oleh AI coding assistant (Antigravity, Claude Code, Codex, dll) saat skill ini di-install.

```markdown
---
name: hgrid247-expert
description: HGrid247-3.5 DE expert skill - Full mastery of the HGrid247 big data ETL platform
---

# HGrid247 Expert Skill

Kamu sekarang adalah expert HGrid247-3.5 DE. Kamu menguasai seluruh aspek platform ini:

## Pengetahuan Inti
- HGrid247 adalah multi-platform, drag-and-drop big data engineering ETL tool
- Workflow pattern: Source → Assembly → Sink
- Supported engines: MapReduce, Spark RDD, Spark 2.x RDD, Spark Dataset, Beam (Batch/Streaming), Flink (Batch/Streaming), Tez, PySpark

## Kemampuan
1. Menjawab pertanyaan tentang HGrid247 berdasarkan dokumentasi di Qdrant
2. Membuat dan menjelaskan workflow (Source → Assembly → Sink)
3. Menjalankan script HGrid via shell
4. Troubleshoot error dan masalah pipeline
5. Membantu konfigurasi dynamic parameter, plugin, dan engine settings

## Tools yang Tersedia
Gunakan tools berikut untuk membantu user:
- `search_docs(query)` — Cari informasi di dokumentasi HGrid247
- `run_hgrid_script(script_content)` — Jalankan bash script untuk HGrid
- `create_workflow(name, source_config, assemblies, sink_config)` — Buat workflow baru
- `list_projects()` — Daftar project HGrid yang tersedia
- `troubleshoot(error_message)` — Analisis dan perbaiki error

## Cara Menggunakan
Untuk menggunakan skill ini, pastikan:
1. Qdrant berjalan di localhost:6333 dengan collection `hgrid247_docs`
2. GOOGLE_API_KEY sudah di-set di environment
3. Jalankan `python ingest.py` terlebih dahulu untuk mengisi data dokumentasi
```

---

#### [NEW] `hgrid_skill/__init__.py`

```python
"""HGrid247 AI Skill Package."""
```

---

#### [NEW] `hgrid_skill/tools/__init__.py`

```python
"""HGrid247 Agent Tools."""
```

---

#### [NEW] `hgrid_skill/tools/hgrid_api.py`
Tool untuk berinteraksi dengan HGrid247.

```python
"""Tools untuk interaksi dengan HGrid247 system."""
from langchain_core.tools import tool
from core.rag import get_vector_store, extract_text_from_response


@tool
def search_docs(query: str) -> str:
    """
    Cari informasi di dokumentasi HGrid247-3.5 DE.
    Gunakan tool ini untuk menjawab pertanyaan tentang fitur,
    cara penggunaan, konfigurasi, dan troubleshooting HGrid247.
    
    Args:
        query: Pertanyaan atau keyword pencarian
    
    Returns:
        Konteks dokumentasi yang relevan
    """
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=5)
    if not results:
        return "Tidak ditemukan informasi relevan di dokumentasi."
    
    output = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "Unknown")
        output.append(f"[{i}] (Sumber: {source})\n{doc.page_content}")
    
    return "\n\n---\n\n".join(output)


@tool
def list_engines() -> str:
    """
    Daftar semua engine/build target yang didukung HGrid247.
    
    Returns:
        Daftar engine beserta output file-nya
    """
    engines = {
        "MapReduce": "<project>_mr.jar",
        "Spark 1.6 RDD": "<project>_spark1.jar",
        "Spark 2.x RDD": "<project>_spark2.jar",
        "Spark 2.x Dataset": "<project>_spark2ds.jar",
        "Beam 2.29.0 (Batch)": "<project>_beam.jar",
        "Beam 2.29.0 (Streaming)": "<project>_sbeam.jar",
        "Flink 1.12.x (Batch)": "<project>_flink.jar",
        "Flink 1.12.x (Streaming)": "<project>_sflink.jar",
        "Tez 0.9.1": "<project>_tez.jar",
        "PySpark": "<flow-name>.py",
    }
    lines = ["Engine HGrid247 yang Tersedia:", ""]
    for engine, output in engines.items():
        lines.append(f"  • {engine} → Output: {output}")
    return "\n".join(lines)
```

---

#### [NEW] `hgrid_skill/tools/script_runner.py`
Tool untuk menjalankan shell script.

```python
"""Tool untuk menjalankan script di sistem."""
import subprocess
from langchain_core.tools import tool


@tool
def run_shell_command(command: str) -> str:
    """
    Jalankan shell command di sistem.
    PERINGATAN: Hanya gunakan untuk perintah yang aman (read-only atau
    perintah yang sudah dikonfirmasi user). Jangan jalankan perintah destruktif
    tanpa konfirmasi.
    
    Args:
        command: Shell command yang akan dijalankan
    
    Returns:
        Output dari command (stdout + stderr)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]: {result.stderr}"
        if result.returncode != 0:
            output += f"\n[EXIT CODE]: {result.returncode}"
        return output or "(tidak ada output)"
    except subprocess.TimeoutExpired:
        return "[ERROR] Command timeout setelah 60 detik"
    except Exception as e:
        return f"[ERROR] {str(e)}"


@tool
def run_hgrid_script(script_content: str) -> str:
    """
    Jalankan shell script untuk HGrid247. Biasanya berisi perintah spark-submit
    atau hadoop jar untuk menjalankan workflow.
    
    Contoh script:
        #!/bin/bash
        spark-submit --class workshop.Lab03 workshop.jar input output
    
    Args:
        script_content: Isi script yang akan dieksekusi
    
    Returns:
        Output eksekusi script
    """
    try:
        result = subprocess.run(
            ["bash", "-c", script_content],
            capture_output=True,
            text=True,
            timeout=300,
        )
        output = f"Script selesai dieksekusi.\n\nOutput:\n{result.stdout}"
        if result.stderr:
            output += f"\nWarnings/Errors:\n{result.stderr}"
        return output
    except subprocess.TimeoutExpired:
        return "[ERROR] Script timeout setelah 5 menit"
    except Exception as e:
        return f"[ERROR] Gagal menjalankan script: {str(e)}"
```

---

#### [NEW] `hgrid_skill/agent.py`
Orchestrator agent yang menggabungkan semua tools.

```python
"""HGrid247 AI Agent - Orchestrator dengan tool calling."""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

from core.config import GEMINI_MODEL
from core.rag import get_vector_store
from core.prompts import AGENT_SYSTEM_PROMPT
from hgrid_skill.tools.hgrid_api import search_docs, list_engines
from hgrid_skill.tools.script_runner import run_shell_command, run_hgrid_script


def create_hgrid_agent():
    """Buat HGrid247 AI Agent dengan semua tools."""
    
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL)
    
    tools = [
        search_docs,
        list_engines,
        run_shell_command,
        run_hgrid_script,
    ]
    
    # Buat ReAct agent menggunakan LangGraph
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=AGENT_SYSTEM_PROMPT,
    )
    
    return agent


def run_agent(query: str, chat_history: list = None):
    """
    Jalankan agent dengan query user.
    
    Args:
        query: Permintaan user
        chat_history: Riwayat percakapan (opsional)
    
    Returns:
        dict: jawaban agent dan tools yang digunakan
    """
    agent = create_hgrid_agent()
    
    messages = []
    if chat_history:
        messages.extend(chat_history)
    messages.append(HumanMessage(content=query))
    
    result = agent.invoke({"messages": messages})
    
    # Ambil pesan terakhir (jawaban agent)
    final_message = result["messages"][-1]
    
    return {
        "jawaban": final_message.content,
        "tools_used": [
            msg.name for msg in result["messages"]
            if hasattr(msg, "name") and msg.name
        ],
    }
```

### Prasyarat Fase 4
```bash
source venv/bin/activate
pip install langgraph
```

### Verifikasi Fase 4

1. **Test agent secara langsung**:
   ```python
   from hgrid_skill.agent import run_agent
   
   # Test tanya jawab (pakai tool search_docs)
   result = run_agent("Apa itu workflow di HGrid247?")
   print(result["jawaban"])
   print(f"Tools used: {result['tools_used']}")
   
   # Test aksi (pakai tool list_engines)
   result = run_agent("Tampilkan semua engine yang didukung HGrid247")
   print(result["jawaban"])
   
   # Test shell command (pakai tool run_shell_command)
   result = run_agent("Cek apakah Java sudah terinstall di sistem ini")
   print(result["jawaban"])
   ```

2. **Integrasi agent ke Streamlit**: Tambahkan toggle di Streamlit untuk beralih antara mode "Q&A" (RAG biasa) dan mode "Agent" (bisa melakukan aksi)

3. **Integrasi agent ke API**: Tambahkan endpoint `POST /api/agent` di FastAPI

---

## Dependency Summary

### `requirements.txt` (Final)

```
# Core LangChain
langchain-core>=1.6.0
langchain-community>=0.4.2
langchain-text-splitters>=1.1.2
langchain-google-genai>=4.3.5
langchain-huggingface>=1.2.2
langchain-qdrant>=1.1.0

# Vector Database
qdrant-client>=1.19.0

# LLM
google-genai>=2.20.0

# Embedding
huggingface_hub>=1.28.0

# Web Scraping (ingest)
beautifulsoup4>=4.12.0

# Environment
python-dotenv>=1.2.0

# Fase 1: Streamlit UI
streamlit>=1.45.0

# Fase 2: FastAPI
fastapi>=0.115.0
uvicorn>=0.34.0

# Fase 4: Agent
langgraph>=0.5.0
```

---

## `.env` (Final)

```env
# Google Gemini API Key
GOOGLE_API_KEY="your-api-key-here"

# Qdrant Configuration
QDRANT_URL="http://localhost:6333"
QDRANT_COLLECTION="hgrid247_docs"

# Model Configuration
EMBEDDING_MODEL="all-MiniLM-L6-v2"
GEMINI_MODEL="gemini-3.6-flash"

# RAG Configuration
SIMILARITY_TOP_K=5
CHUNK_SIZE=700
CHUNK_OVERLAP=100
```

---

## Urutan Eksekusi untuk AI Agent (Codex/Claude/Antigravity)

> [!IMPORTANT]
> Jika kamu adalah AI agent yang membaca dokumen ini, ikuti urutan berikut:

### Pre-requisite Check (Sebelum Memulai)
1. Pastikan `venv/` aktif: `source venv/bin/activate`
2. Pastikan Qdrant running: `docker start qdrant` atau `docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant`
3. Pastikan data sudah ter-ingest: `python ingest.py` (jika collection belum ada)
4. Pastikan `.env` ada dengan `GOOGLE_API_KEY`

### Urutan Implementasi
1. **Buat `core/` package** (`config.py`, `prompts.py`, `rag.py`) — ini fondasi, HARUS dibuat pertama
2. **Refactor `chat.py`** agar menggunakan `core.rag.tanya_hgrid()` — pastikan terminal chat masih berfungsi
3. **Buat `app_streamlit.py`** — install streamlit, test di browser
4. **Buat `api.py`** — install fastapi+uvicorn, test di Swagger UI
5. **Update `core/rag.py`** dengan `tanya_hgrid_with_memory()` — update Streamlit dan API
6. **Buat `hgrid_skill/`** — install langgraph, buat tools dan agent
7. **Buat `requirements.txt`** — freeze semua dependencies
8. **Update `implemetation.md`** — tandai fase yang sudah selesai

### Aturan Penting
- **JANGAN** mengubah `ingest.py` kecuali diminta secara eksplisit
- **JANGAN** mengubah collection name `hgrid247_docs` di Qdrant
- **SELALU** gunakan `core/config.py` untuk konfigurasi, jangan hardcode
- **SELALU** test setiap fase sebelum lanjut ke fase berikutnya
- **SELALU** handle error Gemini response format (list vs string) menggunakan `extract_text_from_response()`
