# Dokumentasi FASE 2: Backend API FastAPI

## Ringkasan

FASE 2 membuat sistem LangChain RAG HGrid247 bisa digunakan oleh aplikasi lain melalui REST API.

Sebelumnya, RAG HGrid247 hanya bisa digunakan dari terminal atau web interface lokal. Dengan FastAPI, frontend atau platform lain bisa mengirim pertanyaan ke backend dan menerima jawaban AI dalam format JSON.

Contoh platform yang bisa menggunakan API ini:

- React web app
- mobile app
- dashboard internal
- portal Solusi247
- chatbot custom
- sistem backend lain

## Arsitektur Sederhana

```text
Web / App / Platform lain
        |
        v
FastAPI Backend
        |
        v
LangChain RAG
        |
        +--> Qdrant untuk mencari dokumentasi HGrid247 yang relevan
        |
        +--> Gemini untuk membuat jawaban AI
```

## Komponen yang Dibuat

File utama yang dibuat pada FASE 2:

```text
api.py
```

File ini berisi backend FastAPI untuk menerima pertanyaan user dan mengembalikan jawaban dari sistem RAG.

## Kebutuhan Agar API Berjalan

Ada tiga komponen yang harus aktif:

### 1. Qdrant

Qdrant digunakan sebagai vector database untuk menyimpan dan mencari dokumen HGrid247 yang sudah di-embedding.

Jalankan Qdrant:

```bash
docker start qdrant
```

### 2. FastAPI Backend

FastAPI digunakan sebagai server API.

Jalankan backend:

```bash
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Setelah berjalan, API bisa diakses di:

```text
http://localhost:8000
```

Swagger UI bisa dibuka di:

```text
http://localhost:8000/docs
```

### 3. Gemini API Key

Gemini digunakan sebagai LLM untuk membuat jawaban berdasarkan konteks dokumentasi dari Qdrant.

Pastikan file `.env` berisi:

```env
GOOGLE_API_KEY=isi_api_key_kamu
```

## Endpoint API

### GET `/health`

Endpoint ini digunakan untuk mengecek apakah backend API aktif.

Contoh request:

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

Kegunaan:

- memastikan server FastAPI berjalan
- melihat collection Qdrant yang digunakan
- melihat model Gemini yang digunakan

### POST `/api/chat`

Endpoint ini digunakan untuk mengirim pertanyaan ke RAG HGrid247.

Contoh request:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"pertanyaan": "Apa itu HGrid247?"}'
```

Contoh body JSON:

```json
{
  "pertanyaan": "Apa itu HGrid247?"
}
```

Contoh response:

```json
{
  "jawaban": "Berdasarkan dokumentasi, HGrid247 adalah ...",
  "sumber": [
    "https://hgridde.labs247.id/dashboard/hgrid247/installation/installation.html"
  ],
  "chunks_used": 5,
  "session_id": "7b6448c4-a41e-4380-8797-ac56605307fe"
}
```

Keterangan response:

- `jawaban`: jawaban AI dari Gemini
- `sumber`: daftar URL dokumentasi yang dipakai sebagai konteks
- `chunks_used`: jumlah potongan dokumen yang dipakai dari Qdrant
- `session_id`: ID sesi chat

## Cara Menggunakan dari Aplikasi Lain

Aplikasi lain cukup mengirim HTTP request ke endpoint:

```text
POST http://localhost:8000/api/chat
```

Contoh JavaScript:

```javascript
const response = await fetch("http://localhost:8000/api/chat", {
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

## Alur Kerja `/api/chat`

Saat user mengirim pertanyaan:

1. FastAPI menerima pertanyaan.
2. Backend memanggil fungsi `tanya_hgrid()` dari `core/rag.py`.
3. LangChain mencari dokumen relevan di Qdrant.
4. Dokumen relevan digabung menjadi konteks.
5. Konteks dan pertanyaan dikirim ke Gemini.
6. Gemini membuat jawaban.
7. FastAPI mengembalikan hasil dalam format JSON.

## Batasan FASE 2

FASE 2 hanya membuat backend API dasar.

Yang belum termasuk di FASE 2:

- memory percakapan
- agent tools
- aksi langsung ke HGrid247
- login atau authentication
- pembatasan CORS production
- database untuk menyimpan riwayat chat

Fitur tersebut masuk ke fase berikutnya.

## Perintah Penting

Install dependency jika belum ada:

```bash
source venv/bin/activate
pip install fastapi uvicorn
```

Jalankan Qdrant:

```bash
docker start qdrant
```

Jalankan API:

```bash
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Buka dokumentasi API:

```text
http://localhost:8000/docs
```

Test health:

```bash
curl http://localhost:8000/health
```

Test chat:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"pertanyaan": "Apa itu Source di HGrid247?"}'
```
