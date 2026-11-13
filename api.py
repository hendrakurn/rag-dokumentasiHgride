"""HGrid247 AI Assistant - FastAPI Backend."""

from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from core.config import GEMINI_MODEL, QDRANT_COLLECTION, SIMILARITY_TOP_K
from core.feedback import save_feedback
from core.knowledge import (
    DEFAULT_CONTEXT_MAX_CHARS,
    MAX_TOP_K,
    build_context_payload,
    ingest_text_knowledge,
    search_knowledge,
)
from core.rag import get_llm, get_vector_store, tanya_hgrid, tanya_hgrid_with_memory
from hgrid_skill.agent import run_agent
from hgrid_skill.tools.workflow_builder import (
    DEFAULT_OUTPUT_DIR,
    _slugify,
    build_workflow_spec,
)


app = FastAPI(
    title="HGrid247 Knowledge and Skill API",
    description="REST API untuk RAG knowledge service dan skill service HGrid247-3.5 DE",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store: Any | None = None
llm: Any | None = None


@app.on_event("startup")
async def startup() -> None:
    """Initialize reusable RAG resources when the API starts."""
    global vector_store, llm
    vector_store = get_vector_store()
    llm = get_llm()


class ChatRequest(BaseModel):
    pertanyaan: str = Field(
        ...,
        min_length=1,
        description="Pertanyaan user tentang HGrid247",
    )
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="ID sesi chat",
    )


class ChatMessage(BaseModel):
    role: str = Field(
        default="",
        description="Role pesan, umumnya user atau assistant",
    )
    content: str | None = Field(
        default="",
        description="Isi pesan percakapan",
    )


class ChatSessionRequest(ChatRequest):
    chat_history: list[ChatMessage] = Field(
        default_factory=list,
        description="Riwayat percakapan sebelumnya",
    )


class ChatResponse(BaseModel):
    jawaban: str
    sumber: list[str]
    chunks_used: int
    session_id: str


class AgentRequest(ChatSessionRequest):
    pass


class AgentResponse(BaseModel):
    jawaban: str
    tools_used: list[str]
    session_id: str


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Query pencarian knowledge HGrid247",
    )
    top_k: int = Field(
        default=min(max(SIMILARITY_TOP_K, 1), MAX_TOP_K),
        ge=1,
        le=MAX_TOP_K,
        description="Jumlah chunk yang diambil dari Qdrant",
    )

    @validator("query")
    def query_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query tidak boleh kosong")
        return value


class SearchResult(BaseModel):
    content: str
    source: str
    score: float | None
    metadata: dict[str, Any]


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    count: int


class ContextRequest(SearchRequest):
    max_chars: int = Field(
        default=DEFAULT_CONTEXT_MAX_CHARS,
        ge=1000,
        le=20000,
        description="Batas maksimal panjang context yang dikembalikan",
    )


class ContextResponse(BaseModel):
    query: str
    context: str
    sources: list[str]
    chunks_used: int


class SkillInfo(BaseModel):
    name: str
    description: str
    category: str


class SkillsResponse(BaseModel):
    skills: list[SkillInfo]


class WorkflowDraftRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    engine: str = "Spark 2.x Dataset"
    source_config: dict[str, Any] = Field(..., min_length=1)
    assemblies: list[dict[str, Any]] = Field(default_factory=list)
    sink_config: dict[str, Any] = Field(..., min_length=1)

    @validator("name")
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name tidak boleh kosong")
        return value


class WorkflowDraftResponse(BaseModel):
    message: str
    path: str
    workflow: dict[str, Any]


class FeedbackRequest(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = ""
    feedback: str = Field(..., min_length=1)
    rating: int | None = Field(default=None, ge=1, le=5)
    source: str = ""
    session_id: str = ""

    @validator("question", "feedback")
    def required_text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field tidak boleh kosong")
        return value


class FeedbackResponse(BaseModel):
    message: str
    path: str


class KnowledgeIngestRequest(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    source: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    @validator("title", "content")
    def ingest_text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field tidak boleh kosong")
        return value


class KnowledgeIngestResponse(BaseModel):
    message: str
    source: str
    chunks_added: int


class HealthResponse(BaseModel):
    status: str
    qdrant: str
    collection: str
    model: str


SKILLS: list[SkillInfo] = [
    SkillInfo(
        name="search_docs",
        description="Cari informasi di dokumentasi HGrid247-3.5 DE.",
        category="knowledge",
    ),
    SkillInfo(
        name="list_engines",
        description="Daftar semua engine/build target yang didukung HGrid247.",
        category="hgrid",
    ),
    SkillInfo(
        name="list_workflow_components",
        description="Daftar source, assembly, sink, dan engine umum untuk workflow.",
        category="workflow",
    ),
    SkillInfo(
        name="create_workflow",
        description="Membuat draft workflow specification JSON.",
        category="workflow",
    ),
    SkillInfo(
        name="run_shell_command",
        description="Menjalankan shell command. Berisiko untuk production.",
        category="execution",
    ),
    SkillInfo(
        name="run_hgrid_script",
        description="Menjalankan shell script HGrid247. Berisiko untuk production.",
        category="execution",
    ),
]


def _chat_response_from_result(hasil: dict[str, Any], session_id: str) -> ChatResponse:
    return ChatResponse(
        jawaban=hasil["jawaban"],
        sumber=hasil["sumber"],
        chunks_used=hasil["chunks_used"],
        session_id=session_id,
    )


def _history_from_messages(messages: list[ChatMessage]) -> list[dict[str, str | None]]:
    return [
        {"role": message.role, "content": message.content}
        for message in messages
    ]


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Cek status kesehatan sistem."""
    return HealthResponse(
        status="healthy",
        qdrant="connected",
        collection=QDRANT_COLLECTION,
        model=GEMINI_MODEL,
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
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
        return _chat_response_from_result(hasil, request.session_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc


@app.post("/api/answer", response_model=ChatResponse)
async def answer(request: ChatRequest) -> ChatResponse:
    """
    Endpoint eksplisit untuk menghasilkan jawaban final dari RAG.

    Endpoint ini setara dengan /api/chat, tetapi memakai nama yang lebih jelas
    untuk service yang memisahkan search, context, dan answer.
    """
    return await chat(request)


@app.post("/api/chat/session", response_model=ChatResponse)
async def chat_with_memory(request: ChatSessionRequest) -> ChatResponse:
    """
    Endpoint tanya-jawab RAG dengan conversational memory.

    API tetap stateless: client menyimpan riwayat percakapan dan mengirimkannya
    lagi pada request berikutnya.
    """
    try:
        history = _history_from_messages(request.chat_history)
        hasil = tanya_hgrid_with_memory(
            request.pertanyaan,
            chat_history=history,
            vector_store=vector_store,
            llm=llm,
        )
        return _chat_response_from_result(hasil, request.session_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc


@app.post("/api/search", response_model=SearchResponse)
async def search_api(request: SearchRequest) -> SearchResponse:
    """
    Ambil chunk knowledge relevan dari Qdrant tanpa memanggil Gemini.

    Endpoint ini cocok untuk project lain yang sudah memiliki LLM sendiri dan
    hanya membutuhkan retrieval result dari knowledge HGrid247.
    """
    try:
        results = search_knowledge(
            request.query,
            top_k=request.top_k,
            vector_store=vector_store,
        )
        return SearchResponse(
            query=request.query,
            results=results,
            count=len(results),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc


@app.post("/api/context", response_model=ContextResponse)
async def context_api(request: ContextRequest) -> ContextResponse:
    """Ambil chunk knowledge dan susun menjadi konteks siap pakai untuk prompt."""
    try:
        payload = build_context_payload(
            request.query,
            top_k=request.top_k,
            max_chars=request.max_chars,
            vector_store=vector_store,
        )
        return ContextResponse(**payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc


@app.get("/api/skills", response_model=SkillsResponse)
async def list_skills() -> SkillsResponse:
    """Daftar skill/tool yang tersedia untuk project lain."""
    return SkillsResponse(skills=SKILLS)


@app.post("/api/workflow/draft", response_model=WorkflowDraftResponse)
async def workflow_draft(request: WorkflowDraftRequest) -> WorkflowDraftResponse:
    """Buat draft workflow HGrid247 tanpa melewati chat agent."""
    try:
        workflow = build_workflow_spec(
            name=request.name,
            source_config=request.source_config,
            assemblies=request.assemblies,
            sink_config=request.sink_config,
            engine=request.engine,
            description=request.description,
        )
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DEFAULT_OUTPUT_DIR / f"{_slugify(workflow['name'])}.workflow.json"
        output_path.write_text(
            json.dumps(workflow, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return WorkflowDraftResponse(
            message="Draft workflow spec created.",
            path=str(output_path),
            workflow=workflow,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc


@app.post("/api/feedback", response_model=FeedbackResponse)
async def feedback_api(request: FeedbackRequest) -> FeedbackResponse:
    """Simpan feedback jawaban sebagai JSONL untuk evaluasi/kurasi berikutnya."""
    try:
        path = save_feedback(
            question=request.question,
            answer=request.answer,
            feedback=request.feedback,
            rating=request.rating,
            source=request.source,
            session_id=request.session_id,
        )
        return FeedbackResponse(message="Feedback saved.", path=path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc


@app.post("/api/knowledge/ingest", response_model=KnowledgeIngestResponse)
async def knowledge_ingest(request: KnowledgeIngestRequest) -> KnowledgeIngestResponse:
    """Tambahkan knowledge text baru ke collection Qdrant yang sudah ada."""
    try:
        result = ingest_text_knowledge(
            title=request.title,
            content=request.content,
            source=request.source,
            metadata=request.metadata,
            vector_store=vector_store,
        )
        return KnowledgeIngestResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc


@app.post("/api/agent", response_model=AgentResponse)
async def agent_chat(request: AgentRequest) -> AgentResponse:
    """
    Endpoint agent HGrid247 dengan tool calling.

    Gunakan endpoint ini ketika user ingin membuat draft workflow, melihat
    daftar engine/komponen, mencari dokumentasi, atau menjalankan aksi tool.
    """
    try:
        history = _history_from_messages(request.chat_history)
        hasil = run_agent(request.pertanyaan, chat_history=history)
        return AgentResponse(
            jawaban=hasil["jawaban"],
            tools_used=hasil["tools_used"],
            session_id=request.session_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error: {exc}") from exc
