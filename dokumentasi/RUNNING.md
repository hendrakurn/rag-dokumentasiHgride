# Menjalankan Web RAG HGrid247

Dokumen ini menjelaskan cara menjalankan dan melihat interface Streamlit untuk sistem RAG HGrid247.

## Prasyarat

Pastikan tersedia:

- Python 3.10 atau lebih baru
- Virtual environment pada folder `venv`
- Service Qdrant yang dapat diakses
- API key Google Gemini
- Collection Qdrant yang sudah berisi hasil ingest dokumen

## Konfigurasi environment

Buat atau periksa file `.env` di root project:

```env
GOOGLE_API_KEY=isi_api_key_gemini
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=hgrid247_docs
EMBEDDING_MODEL=all-MiniLM-L6-v2
GEMINI_MODEL=gemini-3.6-flash
SIMILARITY_TOP_K=5
```

`GOOGLE_API_KEY` wajib diisi. Jangan commit file `.env` atau membagikan API key.

Nilai konfigurasi selain `GOOGLE_API_KEY` memiliki default di `core/config.py`, sehingga hanya perlu ditambahkan ke `.env` jika ingin mengganti default tersebut.

## Instalasi dependency

Dari root project, jalankan:

```bash
cd /home/hendra/projects/solusi247/dokProjekLangchain-1
source venv/bin/activate
python -m pip install -r requirements.txt
```

Jika virtual environment belum tersedia, buat terlebih dahulu:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Menjalankan Qdrant

Jika Qdrant dijalankan secara lokal dengan Docker:

```bash
docker run -d \
  --name hgrid247-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  qdrant/qdrant
```

Pastikan Qdrant dapat diakses di `http://localhost:6333` dan collection pada `QDRANT_COLLECTION` sudah tersedia. Data dapat disiapkan menggunakan alur ingest project sebelum menjalankan chat.

## Menjalankan web

Aktifkan environment lalu jalankan Streamlit:

```bash
cd /home/hendra/projects/solusi247/dokProjekLangchain-1
source venv/bin/activate
streamlit run app_streamlit.py
```

Terminal akan menampilkan alamat web, biasanya:

```text
Local URL: http://localhost:8501
```

Buka alamat tersebut di browser. Jika port `8501` sedang digunakan, gunakan port lain:

```bash
streamlit run app_streamlit.py --server.port 8502
```

Kemudian buka `http://localhost:8502`.

## Menggunakan interface

1. Buka `http://localhost:8501`.
2. Masukkan pertanyaan tentang dokumentasi HGrid247 pada kolom chat.
3. Tekan `Enter` atau tombol kirim.
4. Tunggu proses retrieval dan generation selesai.
5. Periksa jawaban serta bagian sumber yang ditampilkan di bawah respons.

Jawaban dibuat berdasarkan dokumen yang ditemukan di Qdrant. Gunakan bagian sumber untuk memeriksa rujukan jawaban.

## Verifikasi cepat

Periksa apakah server Streamlit aktif:

```bash
curl http://localhost:8501/_stcore/health
```

Respons yang benar:

```text
ok
```

Uji engine RAG langsung dari terminal:

```bash
venv/bin/python -c "from core.rag import tanya_hgrid; r = tanya_hgrid('Apa itu HGrid247?'); print(r['jawaban']); print(r['sumber'])"
```

Perintah ini memerlukan koneksi aktif ke Qdrant dan `GOOGLE_API_KEY` yang valid.

Uji engine RAG dengan memory:

```bash
venv/bin/python -c "from core.rag import tanya_hgrid_with_memory; r = tanya_hgrid_with_memory('Bagaimana cara membuatnya?', [{'role': 'user', 'content': 'Apa itu Source di HGrid247?'}, {'role': 'assistant', 'content': 'Source adalah operator untuk membaca data.'}]); print(r['jawaban']); print(r['sumber'])"
```

Uji endpoint API dengan memory:

```bash
curl -X POST http://localhost:8000/api/chat/session \
  -H "Content-Type: application/json" \
  -d '{"pertanyaan":"Bagaimana cara membuatnya?","session_id":"user-123","chat_history":[{"role":"user","content":"Apa itu Source di HGrid247?"},{"role":"assistant","content":"Source adalah operator untuk membaca data."}]}'
```

Jalankan test Fase 3 tanpa memanggil Qdrant atau Gemini asli:

```bash
venv/bin/python -m unittest tests.test_phase3_memory
```

## Troubleshooting

### `streamlit: command not found`

Pastikan virtual environment sudah aktif, atau jalankan executable secara langsung:

```bash
venv/bin/streamlit run app_streamlit.py
```

### Gagal terhubung ke Qdrant

Periksa hal berikut:

- Qdrant sedang berjalan.
- `QDRANT_URL` menunjuk ke alamat yang benar.
- Port `6333` tidak diblokir.
- Nama `QDRANT_COLLECTION` sama dengan collection hasil ingest.

### `GOOGLE_API_KEY` tidak ditemukan

Pastikan `.env` berada di root project dan memuat:

```env
GOOGLE_API_KEY=isi_api_key_gemini
```

Jangan menambahkan tanda kutip atau spasi yang tidak diperlukan pada nama variable.

### Tidak ada sumber atau jawaban tidak relevan

Kemungkinan collection belum berisi dokumen, isi dokumen belum sesuai pertanyaan, atau embedding yang digunakan saat ingest berbeda dari `EMBEDDING_MODEL`. Jalankan ulang proses ingest dengan konfigurasi embedding yang sama.

### Menghentikan server

Kembali ke terminal yang menjalankan Streamlit, lalu tekan:

```text
Ctrl+C
```

## File penting

- `app_streamlit.py`: interface web Streamlit.
- `core/rag.py`: retrieval, prompt, dan pemanggilan Gemini.
- `core/config.py`: konfigurasi environment dan model.
- `core/prompts.py`: prompt RAG.
- `dokumentasi/FASE3_MEMORY.md`: penjelasan memory dan contoh endpoint session.
- `chat.py`: interface terminal yang memakai engine RAG yang sama.
- `requirements.txt`: dependency Python.
- `implemetation.md`: catatan tahap implementasi project.
