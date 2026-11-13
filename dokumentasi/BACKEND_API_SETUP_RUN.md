# Backend API HGrid247 - Setup, Run, dan Daftar API

Dokumen ini menjelaskan cara menyiapkan backend FastAPI HGrid247, cara menjalankannya, dan endpoint API yang tersedia setelah backend diperluas dari Chat API menjadi RAG Knowledge Service + Skill Service.

## Ringkasan Backend

Backend utama ada di `api.py`.

Sebelumnya backend hanya menyediakan endpoint chat untuk bertanya ke RAG. Sekarang backend juga bisa dipakai oleh project lain untuk mengambil knowledge mentah, mengambil konteks siap prompt, membuat jawaban final, melihat daftar skill/tool, membuat draft workflow, menyimpan feedback, dan menambahkan knowledge text baru ke Qdrant.

Arsitektur umum:

```text
Project lain / Frontend / AI lain
  -> FastAPI Backend
  -> Knowledge Service / Skill Service
  -> Qdrant Vector Database
  -> Gemini LLM jika endpoint membutuhkan jawaban final
  -> JSON response ke client
```

Pemisahan fungsi endpoint:

```text
/api/search          -> retrieval mentah dari Qdrant, tanpa Gemini
/api/context         -> context siap prompt, tanpa Gemini
/api/answer          -> jawaban final dari RAG + Gemini
/api/chat            -> endpoint chat lama, tetap kompatibel
/api/chat/session    -> chat dengan history dari client
/api/skills          -> daftar tool/skill yang tersedia
/api/workflow/draft  -> membuat draft workflow langsung
/api/feedback        -> menyimpan feedback/koreksi
/api/knowledge/ingest -> menambah knowledge text ke Qdrant
/api/agent           -> agent dengan tool calling
/health              -> cek status backend
```

## Komponen yang Perlu Berjalan

Selain Qdrant, komponen yang perlu disiapkan adalah:

1. Python virtual environment project.
2. Dependency Python dari `requirements.txt`.
3. File `.env` yang berisi `GOOGLE_API_KEY`.
4. Collection Qdrant yang sudah diisi data dokumentasi lewat `ingest.py`.
5. Server FastAPI yang dijalankan dengan `uvicorn`.

## Setup Awal

Masuk ke root project:

```bash
cd /home/hendra/projects/solusi247/dokProjekLangchain-1
```

Aktifkan virtual environment:

```bash
source venv/bin/activate
```

Install dependency jika belum pernah:

```bash
pip install -r requirements.txt
```

Buat atau lengkapi file `.env`:

```env
GOOGLE_API_KEY=isi_api_key_gemini
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=hgrid247_docs
GEMINI_MODEL=gemini-3.6-flash
SIMILARITY_TOP_K=10
MAX_HISTORY_MESSAGES=8
```

`GOOGLE_API_KEY` wajib untuk endpoint yang memanggil Gemini, seperti `/api/chat`, `/api/chat/session`, `/api/answer`, dan `/api/agent`. Endpoint `/api/search`, `/api/context`, `/api/skills`, `/api/workflow/draft`, dan `/api/feedback` tidak membutuhkan Gemini secara langsung.

## Menjalankan Qdrant

Jika Qdrant sudah dibuat sebagai container bernama `qdrant`, jalankan:

```bash
docker start qdrant
```

Cek Qdrant:

```bash
curl http://localhost:6333/healthz
```

Backend memakai Qdrant di:

```text
http://localhost:6333
```

Collection default:

```text
hgrid247_docs
```

## Mengisi Data ke Qdrant

Jika collection belum ada, data belum lengkap, atau ingin refresh dokumentasi HGrid247:

```bash
source venv/bin/activate
python ingest.py
```

Script `ingest.py` akan:

1. Membaca dokumentasi HGrid247 dari daftar URL.
2. Memecah dokumen menjadi chunk teks.
3. Membuat embedding menggunakan model `all-MiniLM-L6-v2`.
4. Menyimpan hasil embedding ke Qdrant collection `hgrid247_docs`.

Catatan: `ingest.py` memakai `force_recreate=True`, jadi collection akan dibuat ulang setiap script dijalankan.

## Menjalankan Backend API

Jalankan FastAPI dengan `uvicorn`:

```bash
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Setelah berjalan:

```text
Base URL: http://localhost:8000
Swagger UI: http://localhost:8000/docs
```

Untuk production, jangan gunakan `--reload`.

## Urutan Run dari Nol

```bash
cd /home/hendra/projects/solusi247/dokProjekLangchain-1
source venv/bin/activate
pip install -r requirements.txt
docker start qdrant
python ingest.py
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Jika Qdrant sudah berisi collection `hgrid247_docs`, cukup jalankan:

```bash
docker start qdrant
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Cara Project Lain Menggunakan Backend Ini

Jika project lain memiliki LLM sendiri, gunakan `/api/search` atau `/api/context` untuk mengambil knowledge HGrid247 tanpa meminta backend membuat jawaban final.

Jika project lain tidak memiliki LLM sendiri, gunakan `/api/answer` atau `/api/chat` agar backend langsung mengembalikan jawaban final dari Gemini.

Jika project lain ingin mengetahui kemampuan backend, gunakan `/api/skills`.

Jika project lain ingin membuat draft workflow tanpa percakapan agent, gunakan `/api/workflow/draft`.

Jika project lain ingin memberi koreksi atau penilaian jawaban, gunakan `/api/feedback`.

Jika project lain ingin menambah knowledge text baru, gunakan `/api/knowledge/ingest`. Endpoint ini harus dilindungi jika backend dibuka ke jaringan publik.

Contoh dari laptop atau project lain:

```bash
curl -X POST http://IP_BACKEND:8000/api/context   -H "Content-Type: application/json"   -d '{
    "query": "cara membuat workflow HGrid247",
    "top_k": 5
  }'
```

## Daftar API

### 1. GET `/health`

Digunakan untuk mengecek apakah backend API aktif dan konfigurasi dasar terbaca.

Request:

```bash
curl http://localhost:8000/health
```

Contoh response:

```json
{
  "status": "healthy",
  "qdrant": "connected",
  "collection": "hgrid247_docs",
  "model": "gemini-3.6-flash"
}
```

Kapan digunakan:

- Mengecek server FastAPI berjalan.
- Melihat collection Qdrant yang digunakan.
- Melihat model Gemini yang digunakan.

Catatan: field `qdrant` saat ini dikembalikan sebagai nilai statis dari kode, belum melakukan health check nyata ke Qdrant.

### 2. POST `/api/search`

Mengambil chunk knowledge relevan dari Qdrant tanpa memanggil Gemini.

Request:

```bash
curl -X POST http://localhost:8000/api/search   -H "Content-Type: application/json"   -d '{
    "query": "cara membuat workflow HGrid247",
    "top_k": 5
  }'
```

Body:

```json
{
  "query": "cara membuat workflow HGrid247",
  "top_k": 5
}
```

Contoh response:

```json
{
  "query": "cara membuat workflow HGrid247",
  "results": [
    {
      "content": "Potongan dokumentasi HGrid247 yang relevan.",
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

Kapan digunakan:

- Project lain sudah punya LLM sendiri.
- Project lain hanya butuh chunk mentah dari Qdrant.
- Project lain ingin meranking, memfilter, atau menyusun prompt sendiri.

### 3. POST `/api/context`

Mengambil chunk knowledge dari Qdrant dan menyusunnya menjadi konteks siap dimasukkan ke prompt LLM project lain.

Request:

```bash
curl -X POST http://localhost:8000/api/context   -H "Content-Type: application/json"   -d '{
    "query": "cara membuat workflow HGrid247",
    "top_k": 5,
    "max_chars": 6000
  }'
```

Body:

```json
{
  "query": "cara membuat workflow HGrid247",
  "top_k": 5,
  "max_chars": 6000
}
```

Contoh response:

```json
{
  "query": "cara membuat workflow HGrid247",
  "context": "[1] Source: https://...
Potongan dokumentasi...

---

[2] Source: https://...
Potongan dokumentasi...",
  "sources": [
    "https://hgridde.labs247.id/dashboard/hgrid247/..."
  ],
  "chunks_used": 5
}
```

Kapan digunakan:

- AI di project lain ingin memasukkan knowledge HGrid247 ke prompt mereka sendiri.
- Client tidak ingin menerima banyak object chunk, tetapi ingin satu string context yang rapi.
- Cocok untuk integrasi agent eksternal.

### 4. POST `/api/answer`

Menghasilkan jawaban final dari RAG + Gemini. Endpoint ini adalah versi eksplisit dari `/api/chat`.

Request:

```bash
curl -X POST http://localhost:8000/api/answer   -H "Content-Type: application/json"   -d '{
    "pertanyaan": "Apa itu HGrid247?",
    "session_id": "demo-1"
  }'
```

Body:

```json
{
  "pertanyaan": "Apa itu HGrid247?",
  "session_id": "demo-1"
}
```

Contoh response:

```json
{
  "jawaban": "Jawaban dari Gemini berdasarkan dokumentasi HGrid247.",
  "sumber": [
    "https://hgridde.labs247.id/dashboard/hgrid247/..."
  ],
  "chunks_used": 10,
  "session_id": "demo-1"
}
```

Kapan digunakan:

- Project lain tidak punya LLM sendiri.
- Client ingin jawaban final, bukan context mentah.
- Integrasi membutuhkan nama endpoint yang jelas untuk fungsi answer.

### 5. POST `/api/chat`

Endpoint tanya-jawab RAG lama tanpa memory percakapan. Endpoint ini tetap dipertahankan untuk backward compatibility.

Request:

```bash
curl -X POST http://localhost:8000/api/chat   -H "Content-Type: application/json"   -d '{
    "pertanyaan": "Apa itu HGrid247?"
  }'
```

Body:

```json
{
  "pertanyaan": "Apa itu HGrid247?",
  "session_id": "opsional-session-id"
}
```

Contoh response:

```json
{
  "jawaban": "Jawaban dari Gemini berdasarkan dokumentasi HGrid247.",
  "sumber": [
    "https://hgridde.labs247.id/dashboard/hgrid247/..."
  ],
  "chunks_used": 10,
  "session_id": "opsional-session-id"
}
```

Kapan digunakan:

- Chatbot dokumentasi HGrid247.
- Tanya-jawab teknis dari frontend.
- Integrasi lama yang sudah memakai `/api/chat`.

### 6. POST `/api/chat/session`

Endpoint tanya-jawab RAG dengan memory percakapan. Backend tetap stateless, sehingga client harus mengirim `chat_history` pada setiap request lanjutan.

Request:

```bash
curl -X POST http://localhost:8000/api/chat/session   -H "Content-Type: application/json"   -d '{
    "session_id": "demo-1",
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

Body:

```json
{
  "pertanyaan": "Bagaimana cara menjalankannya?",
  "session_id": "demo-1",
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
}
```

Role yang valid untuk memory:

```text
user
assistant
```

Contoh response:

```json
{
  "jawaban": "Jawaban lanjutan berdasarkan pertanyaan dan history.",
  "sumber": [
    "https://hgridde.labs247.id/dashboard/hgrid247/..."
  ],
  "chunks_used": 8,
  "session_id": "demo-1"
}
```

Kapan digunakan:

- Chat multi-turn.
- Pertanyaan lanjutan seperti "jelaskan bagian itu lagi".
- UI chatbot yang menyimpan history di browser atau database client.

### 7. GET `/api/skills`

Mengembalikan daftar skill/tool yang tersedia untuk project lain.

Request:

```bash
curl http://localhost:8000/api/skills
```

Contoh response:

```json
{
  "skills": [
    {
      "name": "search_docs",
      "description": "Cari informasi di dokumentasi HGrid247-3.5 DE.",
      "category": "knowledge"
    },
    {
      "name": "list_engines",
      "description": "Daftar semua engine/build target yang didukung HGrid247.",
      "category": "hgrid"
    },
    {
      "name": "create_workflow",
      "description": "Membuat draft workflow specification JSON.",
      "category": "workflow"
    }
  ]
}
```

Kapan digunakan:

- Project lain ingin menampilkan kemampuan backend.
- Agent eksternal ingin tahu tool apa saja yang tersedia.
- Frontend ingin membuat UI berdasarkan daftar skill.

### 8. POST `/api/workflow/draft`

Membuat draft workflow HGrid247 tanpa harus lewat chat agent.

Request:

```bash
curl -X POST http://localhost:8000/api/workflow/draft   -H "Content-Type: application/json"   -d '{
    "name": "demo workflow",
    "description": "Workflow contoh",
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

Body:

```json
{
  "name": "demo workflow",
  "description": "Workflow contoh",
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
}
```

Contoh response:

```json
{
  "message": "Draft workflow spec created.",
  "path": "generated_workflows/demo-workflow.workflow.json",
  "workflow": {
    "schema": "hgrid247.workflow.draft.v1",
    "status": "draft_spec",
    "name": "demo workflow",
    "engine": "Spark 2.x Dataset",
    "nodes": [],
    "edges": [],
    "warnings": []
  }
}
```

Kapan digunakan:

- Project lain ingin membuat draft workflow secara programmatic.
- Frontend ingin menyediakan form Source -> Assembly -> Sink.
- Client ingin output workflow JSON tanpa percakapan agent.

Catatan: output masih draft workflow spec, belum native `.csd` HGrid.

### 9. POST `/api/feedback`

Menyimpan feedback dari project/user lain sebagai JSONL lokal di `data/feedback.jsonl`.

Request:

```bash
curl -X POST http://localhost:8000/api/feedback   -H "Content-Type: application/json"   -d '{
    "question": "Apa itu HGrid247?",
    "answer": "Jawaban sebelumnya.",
    "feedback": "Jawaban kurang menyebut workflow.",
    "rating": 3,
    "source": "project-a",
    "session_id": "demo-1"
  }'
```

Body:

```json
{
  "question": "Apa itu HGrid247?",
  "answer": "Jawaban sebelumnya.",
  "feedback": "Jawaban kurang menyebut workflow.",
  "rating": 3,
  "source": "project-a",
  "session_id": "demo-1"
}
```

Contoh response:

```json
{
  "message": "Feedback saved.",
  "path": "data/feedback.jsonl"
}
```

Kapan digunakan:

- Project lain ingin menyimpan koreksi user.
- Tim ingin mengumpulkan data evaluasi jawaban.
- Feedback akan dipakai untuk kurasi knowledge atau evaluasi RAG berikutnya.

Catatan: endpoint ini tidak otomatis mengubah model atau embedding. Feedback hanya disimpan sebagai sinyal evaluasi.

### 10. POST `/api/knowledge/ingest`

Menambahkan knowledge text baru ke collection Qdrant yang sudah ada. Endpoint ini tidak melakukan `force_recreate`, sehingga tidak menghapus data lama.

Request:

```bash
curl -X POST http://localhost:8000/api/knowledge/ingest   -H "Content-Type: application/json"   -d '{
    "title": "Catatan internal workflow",
    "content": "Isi knowledge baru tentang workflow HGrid247.",
    "source": "project-a/manual-note",
    "metadata": {
      "project": "project-a"
    }
  }'
```

Body:

```json
{
  "title": "Catatan internal workflow",
  "content": "Isi knowledge baru tentang workflow HGrid247.",
  "source": "project-a/manual-note",
  "metadata": {
    "project": "project-a"
  }
}
```

Contoh response:

```json
{
  "message": "Knowledge ingested.",
  "source": "project-a/manual-note",
  "chunks_added": 3
}
```

Kapan digunakan:

- Project lain ingin menambah catatan internal.
- Knowledge baru belum ada di dokumentasi web HGrid247.
- Tim ingin menambahkan informasi manual tanpa menjalankan ulang `ingest.py`.

Catatan keamanan: endpoint ini harus dilindungi dengan authentication/authorization jika backend dapat diakses publik. Tanpa proteksi, siapa pun dapat mencemari knowledge base.

### 11. POST `/api/agent`

Endpoint agent HGrid247 dengan tool calling. Endpoint ini dipakai untuk kebutuhan yang lebih luas dari RAG biasa.

Request:

```bash
curl -X POST http://localhost:8000/api/agent   -H "Content-Type: application/json"   -d '{
    "session_id": "agent-demo-1",
    "pertanyaan": "Buatkan draft workflow HfsSource ke HfsSink dengan Spark 2.x Dataset",
    "chat_history": []
  }'
```

Body:

```json
{
  "pertanyaan": "Buatkan draft workflow HfsSource ke HfsSink dengan Spark 2.x Dataset",
  "session_id": "agent-demo-1",
  "chat_history": []
}
```

Contoh response:

```json
{
  "jawaban": "Jawaban agent.",
  "tools_used": [
    "create_workflow"
  ],
  "session_id": "agent-demo-1"
}
```

Tools yang tersedia untuk agent:

- `search_docs`: mencari informasi di dokumentasi HGrid247 lewat Qdrant.
- `list_engines`: menampilkan daftar engine/build target HGrid247.
- `list_workflow_components`: menampilkan source, assembly, sink, dan engine umum.
- `create_workflow`: membuat draft workflow JSON di folder `generated_workflows`.
- `run_shell_command`: menjalankan shell command.
- `run_hgrid_script`: menjalankan shell script HGrid247.

Kapan digunakan:

- Membantu menyusun workflow HGrid247 secara conversational.
- Melihat daftar engine yang didukung.
- Mencari dokumentasi teknis dengan tool.
- Menjalankan script HGrid247 setelah perintah aman dikonfirmasi.

Catatan keamanan: `run_shell_command` dan `run_hgrid_script` dapat menjalankan command di sistem. Untuk production, endpoint ini perlu authentication, authorization, allowlist command, audit log, dan pembatasan akses.

## Format Model Request dan Response

### `SearchRequest`

Dipakai oleh `/api/search` dan menjadi dasar `/api/context`.

```json
{
  "query": "string wajib",
  "top_k": 5
}
```

`top_k` dibatasi dari 1 sampai 20.

### `ContextRequest`

Dipakai oleh `/api/context`.

```json
{
  "query": "string wajib",
  "top_k": 5,
  "max_chars": 6000
}
```

`max_chars` dibatasi dari 1000 sampai 20000.

### `ChatRequest`

Dipakai oleh `/api/chat` dan `/api/answer`.

```json
{
  "pertanyaan": "string wajib",
  "session_id": "string opsional"
}
```

### `ChatSessionRequest`

Dipakai oleh `/api/chat/session` dan menjadi dasar `/api/agent`.

```json
{
  "pertanyaan": "string wajib",
  "session_id": "string opsional",
  "chat_history": [
    {
      "role": "user",
      "content": "isi pesan"
    }
  ]
}
```

### `ChatResponse`

Response dari `/api/chat`, `/api/chat/session`, dan `/api/answer`.

```json
{
  "jawaban": "string",
  "sumber": ["string"],
  "chunks_used": 10,
  "session_id": "string"
}
```

### `FeedbackRequest`

Dipakai oleh `/api/feedback`.

```json
{
  "question": "string wajib",
  "answer": "string opsional",
  "feedback": "string wajib",
  "rating": 3,
  "source": "string opsional",
  "session_id": "string opsional"
}
```

`rating` opsional dan dibatasi dari 1 sampai 5.

### `KnowledgeIngestRequest`

Dipakai oleh `/api/knowledge/ingest`.

```json
{
  "title": "string wajib",
  "content": "string wajib",
  "source": "string opsional",
  "metadata": {}
}
```

### `AgentResponse`

Response dari `/api/agent`.

```json
{
  "jawaban": "string",
  "tools_used": ["string"],
  "session_id": "string"
}
```

## Contoh Penggunaan dari JavaScript

Mengambil context untuk LLM project lain:

```javascript
const response = await fetch("http://localhost:8000/api/context", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "Bagaimana cara membuat workflow di HGrid247?",
    top_k: 5,
  }),
});

const data = await response.json();
console.log(data.context);
console.log(data.sources);
```

Mengambil jawaban final dari backend:

```javascript
const response = await fetch("http://localhost:8000/api/answer", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    pertanyaan: "Bagaimana cara membuat workflow di HGrid247?",
  }),
});

const data = await response.json();
console.log(data.jawaban);
console.log(data.sumber);
```

## Catatan Keamanan Production

Backend saat ini belum memiliki authentication. Jika ingin dipakai di server atau dibuka untuk project lain, minimal tambahkan:

1. API key atau JWT untuk setiap request.
2. CORS yang dibatasi ke domain/client yang dipercaya.
3. Rate limit untuk mencegah abuse.
4. Audit log untuk endpoint penting.
5. Proteksi khusus untuk `/api/knowledge/ingest` agar knowledge tidak tercemar.
6. Proteksi ketat atau penonaktifan tool `run_shell_command` dan `run_hgrid_script` pada `/api/agent`.

Endpoint paling berisiko:

- `/api/agent`, karena agent bisa memakai script runner.
- `/api/knowledge/ingest`, karena dapat menambah data ke knowledge base.
- `/api/feedback`, karena dapat menghasilkan data evaluasi yang perlu dijaga kualitasnya.

## Troubleshooting

### Backend gagal start

Cek dependency:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### API error saat menjawab

Cek hal berikut:

- `GOOGLE_API_KEY` sudah ada di `.env`.
- Qdrant berjalan di `http://localhost:6333`.
- Collection `hgrid247_docs` sudah dibuat oleh `python ingest.py`.
- Nama collection di `.env` sama dengan collection yang ada di Qdrant.

### `/api/search` atau `/api/context` kosong

Kemungkinan penyebab:

- Data belum di-ingest ke Qdrant.
- Collection salah.
- Dokumentasi sumber belum mencakup topik yang ditanyakan.
- Query terlalu umum atau terlalu jauh dari istilah dokumentasi.

### `/api/knowledge/ingest` gagal

Cek hal berikut:

- Qdrant berjalan.
- Collection target tersedia.
- Body memiliki `title` dan `content` yang tidak kosong.
- Metadata berupa object JSON, bukan string.

### `/api/agent` terlalu berisiko untuk production

Endpoint agent memiliki tools eksekusi command. Untuk production, batasi atau matikan tool berikut jika belum ada kontrol keamanan:

- `run_shell_command`
- `run_hgrid_script`
