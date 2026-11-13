# Konteks untuk AI Agent Project Lain: Menggunakan HGrid247 RAG API

## Peran API

Project `dokProjekLangchain-1` menyediakan backend API untuk sistem RAG dokumentasi HGrid247.

API ini sudah menggabungkan:

- LangChain sebagai orchestration RAG
- Qdrant sebagai vector database dokumentasi HGrid247
- Gemini sebagai LLM untuk membuat jawaban
- FastAPI sebagai backend HTTP API

Project lain tidak perlu menjalankan LangChain, Qdrant client, embedding model, atau Gemini secara langsung. Project lain cukup memanggil endpoint HTTP dari backend ini.

## Base URL

Jika backend berjalan di komputer yang sama:

```text
http://localhost:8000
```

Jika backend berjalan di server lain, ganti `localhost` dengan IP atau domain server tersebut:

```text
http://SERVER_IP_OR_DOMAIN:8000
```

## Syarat Backend Harus Aktif

Sebelum project lain memanggil API ini, backend HGrid247 RAG harus berjalan.

Di folder backend:

```bash
cd /home/hendra/projects/solusi247/dokProjekLangchain-1
docker start qdrant
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Jika ada perubahan resource link di `ingest.py`, jalankan ulang ingestion:

```bash
cd /home/hendra/projects/solusi247/dokProjekLangchain-1
docker start qdrant
source venv/bin/activate
python ingest.py
```

Setelah ingestion selesai, restart backend API.

## Endpoint Health Check

Gunakan endpoint ini untuk mengecek apakah API hidup:

```http
GET /health
```

Contoh:

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

## Endpoint Chat RAG

Gunakan endpoint ini untuk mengirim pertanyaan tentang HGrid247:

```http
POST /api/chat
```

Request body:

```json
{
  "pertanyaan": "Apa itu HGrid247?"
}
```

Optional request body dengan session ID:

```json
{
  "pertanyaan": "Apa itu Source di HGrid247?",
  "session_id": "user-session-123"
}
```

Contoh response:

```json
{
  "jawaban": "Berdasarkan dokumentasi, ...",
  "sumber": [
    "https://hgridde.labs247.id/dashboard/hgrid247/menu/source.html"
  ],
  "chunks_used": 10,
  "session_id": "user-session-123"
}
```

Makna field response:

- `jawaban`: jawaban AI berdasarkan dokumentasi HGrid247
- `sumber`: URL dokumentasi yang dipakai sebagai referensi
- `chunks_used`: jumlah potongan dokumen dari Qdrant yang dipakai sebagai konteks
- `session_id`: ID sesi yang dikirim atau dibuat otomatis oleh API

## Endpoint Chat dengan Memory

Gunakan endpoint ini untuk pertanyaan lanjutan yang butuh riwayat percakapan:

```http
POST /api/chat/session
```

Request body:

```json
{
  "pertanyaan": "Bagaimana cara membuatnya?",
  "session_id": "user-session-123",
  "chat_history": [
    {
      "role": "user",
      "content": "Apa itu Source di HGrid247?"
    },
    {
      "role": "assistant",
      "content": "Source adalah operator untuk membaca data."
    }
  ]
}
```

Catatan penting:

- API tetap stateless.
- Client menyimpan `chat_history`, lalu mengirimkannya kembali saat bertanya.
- Server hanya memakai beberapa pesan terakhir sesuai `MAX_HISTORY_MESSAGES`.
- `session_id` belum menyimpan percakapan di database.

## Cara Memanggil dari JavaScript atau React

```javascript
async function askHGrid(pertanyaan) {
  const response = await fetch("http://localhost:8000/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ pertanyaan }),
  });

  if (!response.ok) {
    throw new Error(`HGrid API error: ${response.status}`);
  }

  return await response.json();
}

const result = await askHGrid("Bagaimana cara membuat workflow di HGrid247?");
console.log(result.jawaban);
console.log(result.sumber);
```

## Cara Memanggil dari Python

```python
import requests


def ask_hgrid(pertanyaan: str) -> dict:
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={"pertanyaan": pertanyaan},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


result = ask_hgrid("Apa itu Assembly di HGrid247?")
print(result["jawaban"])
print(result["sumber"])
```

## Instruksi untuk AI Agent di Project Lain

Gunakan instruksi berikut jika agent di project lain perlu memanfaatkan HGrid247 RAG API:

```text
Kamu memiliki akses ke backend HGrid247 RAG API.

Gunakan API ini untuk menjawab pertanyaan tentang dokumentasi HGrid247, workflow, source, assembly, sink, engine, instalasi, troubleshooting, optimasi, dan topik lain yang tersedia di dokumentasi HGrid247.

Base URL default:
http://localhost:8000

Endpoint utama tanpa memory:
POST /api/chat

Endpoint dengan memory:
POST /api/chat/session

Request JSON:
{
  "pertanyaan": "<pertanyaan user tentang HGrid247>"
}

Request JSON dengan memory:
{
  "pertanyaan": "<pertanyaan lanjutan>",
  "session_id": "<id sesi>",
  "chat_history": [
    {"role": "user", "content": "<pertanyaan sebelumnya>"},
    {"role": "assistant", "content": "<jawaban sebelumnya>"}
  ]
}

Response JSON:
{
  "jawaban": "...",
  "sumber": ["..."],
  "chunks_used": 10,
  "session_id": "..."
}

Saat user bertanya tentang HGrid247, jangan mengarang jawaban dari pengetahuan umum. Untuk pertanyaan pertama, panggil endpoint /api/chat. Untuk pertanyaan lanjutan yang memakai konteks percakapan, panggil endpoint /api/chat/session. Gunakan field "jawaban" sebagai jawaban utama, dan tampilkan field "sumber" jika user membutuhkan referensi.

Jika API tidak bisa diakses, beri tahu user bahwa backend HGrid247 RAG belum aktif. Minta user memastikan Qdrant dan FastAPI backend sudah berjalan.

Jangan meminta project lain untuk mengakses Qdrant atau Gemini langsung. Semua akses RAG HGrid247 harus lewat backend API ini.
```

## Error yang Umum Terjadi

### API tidak bisa diakses

Kemungkinan:

- FastAPI belum berjalan
- port bukan `8000`
- project lain menggunakan URL yang salah
- backend berjalan di server berbeda, tapi masih memakai `localhost`

Cek:

```bash
curl http://localhost:8000/health
```

### Jawaban error dari `/api/chat`

Kemungkinan:

- Qdrant belum aktif
- collection `hgrid247_docs` belum ada
- `python ingest.py` belum dijalankan
- `GOOGLE_API_KEY` belum ada di `.env`
- Gemini API bermasalah

### Resource link baru belum muncul di jawaban

Jalankan ulang:

```bash
python ingest.py
```

Lalu restart FastAPI backend.

## Catatan FASE 3

API sudah memiliki conversational memory lewat `/api/chat/session`, tetapi belum menyimpan riwayat di server. `session_id` tetap hanya identitas sesi. Penyimpanan percakapan di Redis atau database bisa ditambahkan pada fase berikutnya jika dibutuhkan.
