# Agent External HGrid API Guide

Dokumen ini adalah source of truth untuk agent atau project lain yang ingin memakai HGrid247 Knowledge and Skill API.

Gunakan dokumen ini saat membuat tool/function calling, MCP wrapper, plugin, custom agent, frontend, atau backend lain yang perlu mengambil knowledge HGrid247 dari service ini.

## Tujuan Integrasi

HGrid247 API menyediakan akses ke knowledge dan skill HGrid247 melalui HTTP. Agent eksternal tidak perlu meng-copy source code backend ini dan tidak perlu mengetahui isi Qdrant secara langsung.

Agent eksternal cukup mengetahui:

```text
Base URL: http://IP_BACKEND:8000
```

atau jika sudah deploy:

```text
Base URL: https://hgrid-api.domain.com
```

## Arsitektur

```text
Agent / Project Eksternal
  -> HTTP request ke HGrid247 API
  -> FastAPI Backend
  -> Qdrant untuk retrieval knowledge
  -> Gemini jika endpoint meminta jawaban final
  -> JSON response ke agent eksternal
```

## Prinsip Pemakaian

Pilih endpoint berdasarkan kebutuhan agent:

```text
Butuh chunk knowledge mentah       -> POST /api/search
Butuh context siap prompt          -> POST /api/context
Butuh jawaban final dari backend   -> POST /api/answer atau POST /api/chat
Butuh chat lanjutan dengan history -> POST /api/chat/session
Butuh tahu kemampuan backend       -> GET /api/skills
Butuh membuat draft workflow       -> POST /api/workflow/draft
Butuh menyimpan feedback/koreksi   -> POST /api/feedback
Butuh menambah knowledge text      -> POST /api/knowledge/ingest
Butuh agent tool calling internal  -> POST /api/agent
```

Untuk agent yang sudah punya LLM sendiri, endpoint paling penting adalah `/api/context` dan `/api/search`.

Untuk agent yang tidak punya LLM sendiri, endpoint paling sederhana adalah `/api/answer`.

## Discovery Endpoint

Agent dapat melihat daftar skill/tool yang tersedia lewat:

```bash
curl http://IP_BACKEND:8000/api/skills
```

Untuk schema lengkap FastAPI:

```text
http://IP_BACKEND:8000/openapi.json
```

Untuk UI dokumentasi interaktif:

```text
http://IP_BACKEND:8000/docs
```

## Endpoint Reference

### GET `/health`

Gunakan untuk mengecek backend aktif.

```bash
curl http://IP_BACKEND:8000/health
```

Response:

```json
{
  "status": "healthy",
  "qdrant": "connected",
  "collection": "hgrid247_docs",
  "model": "gemini-3.6-flash"
}
```

Catatan: field `qdrant` saat ini statis dari backend, belum health check nyata ke Qdrant.

### POST `/api/search`

Gunakan ketika agent eksternal ingin mendapatkan chunk knowledge mentah dari Qdrant tanpa jawaban Gemini.

Request:

```bash
curl -X POST http://IP_BACKEND:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cara membuat workflow HGrid247",
    "top_k": 5
  }'
```

Response:

```json
{
  "query": "cara membuat workflow HGrid247",
  "results": [
    {
      "content": "Potongan dokumentasi relevan.",
      "source": "https://hgridde.labs247.id/dashboard/hgrid247/...",
      "score": 0.82,
      "metadata": {
        "source": "https://hgridde.labs247.id/dashboard/hgrid247/..."
      }
    }
  ],
  "count": 1
}
```

Gunakan endpoint ini jika agent ingin menyusun prompt sendiri, memilih chunk tertentu, melakukan reranking, atau menggabungkan knowledge HGrid247 dengan knowledge lain.

### POST `/api/context`

Gunakan ketika agent eksternal membutuhkan satu string context siap dimasukkan ke prompt LLM.

Request:

```bash
curl -X POST http://IP_BACKEND:8000/api/context \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cara membuat workflow HGrid247",
    "top_k": 5,
    "max_chars": 6000
  }'
```

Response:

```json
{
  "query": "cara membuat workflow HGrid247",
  "context": "[1] Source: https://...\nPotongan dokumentasi...\n\n---\n\n[2] Source: https://...\nPotongan dokumentasi...",
  "sources": [
    "https://hgridde.labs247.id/dashboard/hgrid247/..."
  ],
  "chunks_used": 5
}
```

Recommended usage untuk agent yang punya LLM sendiri:

```text
1. Ambil context dari /api/context.
2. Masukkan context ke prompt agent.
3. Jawab user hanya berdasarkan context tersebut.
4. Tampilkan sources jika user meminta referensi.
5. Jika context kosong, jangan mengarang. Katakan knowledge belum tersedia.
```

### POST `/api/answer`

Gunakan ketika agent eksternal ingin backend HGrid247 membuat jawaban final.

```bash
curl -X POST http://IP_BACKEND:8000/api/answer \
  -H "Content-Type: application/json" \
  -d '{
    "pertanyaan": "Apa itu HGrid247?",
    "session_id": "external-agent-1"
  }'
```

Response:

```json
{
  "jawaban": "Jawaban final berdasarkan RAG HGrid247.",
  "sumber": [
    "https://hgridde.labs247.id/dashboard/hgrid247/..."
  ],
  "chunks_used": 10,
  "session_id": "external-agent-1"
}
```

Gunakan endpoint ini jika agent eksternal tidak punya LLM sendiri atau ingin menyerahkan proses answer generation ke backend HGrid247.

### POST `/api/chat`

Endpoint lama untuk jawaban final tanpa memory. Fungsinya sama dengan `/api/answer`, tetapi dipertahankan untuk backward compatibility.

```bash
curl -X POST http://IP_BACKEND:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "pertanyaan": "Apa itu HGrid247?"
  }'
```

### POST `/api/chat/session`

Gunakan untuk chat lanjutan dengan history dari client. Backend tidak menyimpan session di database, jadi agent eksternal harus mengirim `chat_history` setiap request.

```bash
curl -X POST http://IP_BACKEND:8000/api/chat/session \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "external-agent-1",
    "pertanyaan": "Bagaimana cara menjalankannya?",
    "chat_history": [
      {
        "role": "user",
        "content": "Apa itu HGrid247?"
      },
      {
        "role": "assistant",
        "content": "HGrid247 adalah platform data engineering."
      }
    ]
  }'
```

Role valid:

```text
user
assistant
```

### GET `/api/skills`

Gunakan agar agent eksternal tahu kemampuan backend.

```bash
curl http://IP_BACKEND:8000/api/skills
```

Response berisi skill seperti `search_docs`, `list_engines`, `list_workflow_components`, `create_workflow`, `run_shell_command`, dan `run_hgrid_script`.

### POST `/api/workflow/draft`

Gunakan untuk membuat draft workflow HGrid247 langsung dari JSON.

```bash
curl -X POST http://IP_BACKEND:8000/api/workflow/draft \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo workflow",
    "description": "Workflow contoh dari agent eksternal",
    "engine": "Spark 2.x Dataset",
    "source_config": {
      "type": "HfsSource",
      "path": "/data/input"
    },
    "assemblies": [
      {
        "type": "Filter",
        "condition": "status = ACTIVE"
      }
    ],
    "sink_config": {
      "type": "HfsSink",
      "path": "/data/output"
    }
  }'
```

Output masih draft JSON, belum native `.csd` HGrid.

### POST `/api/feedback`

Gunakan untuk menyimpan koreksi, rating, atau catatan evaluasi dari agent/project eksternal.

```bash
curl -X POST http://IP_BACKEND:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Apa itu HGrid247?",
    "answer": "Jawaban sebelumnya.",
    "feedback": "Jawaban kurang menyebut workflow.",
    "rating": 3,
    "source": "project-a",
    "session_id": "external-agent-1"
  }'
```

Response:

```json
{
  "message": "Feedback saved.",
  "path": "data/feedback.jsonl"
}
```

Feedback tidak otomatis membuat model belajar. Data ini dipakai untuk evaluasi, kurasi, atau improvement berikutnya.

### POST `/api/knowledge/ingest`

Gunakan untuk menambahkan knowledge text baru ke Qdrant tanpa menghapus data lama.

```bash
curl -X POST http://IP_BACKEND:8000/api/knowledge/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Catatan internal workflow",
    "content": "Isi knowledge baru tentang workflow HGrid247.",
    "source": "project-a/manual-note",
    "metadata": {
      "project": "project-a",
      "added_by": "external-agent"
    }
  }'
```

Gunakan endpoint ini untuk menambah catatan internal, dokumentasi tambahan, atau knowledge manual. Jangan gunakan endpoint ini tanpa authentication jika backend terbuka ke network publik.

### POST `/api/agent`

Gunakan jika agent eksternal ingin menyerahkan eksekusi ke agent internal HGrid247 yang punya tool calling.

```bash
curl -X POST http://IP_BACKEND:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "external-agent-1",
    "pertanyaan": "Buatkan draft workflow HfsSource ke HfsSink dengan Spark 2.x Dataset",
    "chat_history": []
  }'
```

Endpoint ini paling berisiko jika dibuka publik karena agent internal memiliki tool eksekusi command/script.

## Recommended Agent Flow

### Agent Punya LLM Sendiri

```text
1. User bertanya tentang HGrid247.
2. Agent panggil POST /api/context dengan query user.
3. Agent masukkan response.context ke prompt LLM.
4. Agent jawab berdasarkan context.
5. Agent tampilkan response.sources jika perlu.
6. Jika user memberi koreksi, agent panggil POST /api/feedback.
```

Prompt pattern:

```text
Gunakan konteks HGrid247 berikut sebagai sumber utama.
Jika konteks kosong atau tidak relevan, katakan bahwa informasi belum tersedia di knowledge HGrid247.

Konteks:
{context}

Pertanyaan user:
{question}
```

### Agent Tidak Punya LLM Sendiri

```text
1. User bertanya tentang HGrid247.
2. Agent panggil POST /api/answer.
3. Agent tampilkan response.jawaban.
4. Agent tampilkan response.sumber jika perlu.
```

### Agent Ingin Membuat Workflow

```text
1. Kumpulkan minimal source_config, assemblies, sink_config, dan engine.
2. Jika data lengkap, panggil POST /api/workflow/draft.
3. Tampilkan path dan ringkasan workflow.
4. Jelaskan bahwa output masih draft JSON, belum native .csd.
```

### Agent Ingin Menambah Knowledge

```text
1. Pastikan content berasal dari sumber yang dipercaya.
2. Panggil POST /api/knowledge/ingest.
3. Simpan source dan metadata yang jelas.
4. Jangan ingest data sensitif atau tidak tervalidasi.
```

## Contoh Tool Wrapper Python

```python
import requests


class HGridKnowledgeClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def context(self, query: str, top_k: int = 5, max_chars: int = 6000) -> dict:
        response = requests.post(
            f"{self.base_url}/api/context",
            json={"query": query, "top_k": top_k, "max_chars": max_chars},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def answer(self, question: str, session_id: str = "") -> dict:
        payload = {"pertanyaan": question}
        if session_id:
            payload["session_id"] = session_id
        response = requests.post(
            f"{self.base_url}/api/answer",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def save_feedback(self, question: str, feedback: str, **kwargs) -> dict:
        payload = {"question": question, "feedback": feedback, **kwargs}
        response = requests.post(
            f"{self.base_url}/api/feedback",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
```

## Rules for Agent Eksternal

Agent eksternal harus mengikuti aturan ini:

1. Jangan mengarang jawaban teknis HGrid247 jika context kosong.
2. Untuk pertanyaan teknis HGrid247, panggil `/api/context` sebelum menjawab jika agent punya LLM sendiri.
3. Gunakan `/api/answer` jika ingin jawaban final dari backend HGrid247.
4. Tampilkan atau simpan `sources` saat jawaban perlu audit trail.
5. Gunakan `/api/feedback` saat user mengoreksi jawaban.
6. Jangan panggil `/api/knowledge/ingest` untuk data yang belum dipercaya.
7. Jangan expose `/api/agent` dan `/api/knowledge/ingest` ke publik tanpa authentication.

## Production Security Notes

Backend saat ini belum memiliki authentication bawaan. Jika dipakai oleh project lain di jaringan bersama atau internet, tambahkan:

- API key atau JWT.
- CORS yang dibatasi.
- Rate limit.
- Audit log.
- Permission per endpoint.
- Proteksi khusus untuk `/api/knowledge/ingest`.
- Proteksi atau penonaktifan script runner pada `/api/agent`.

