# Dokumentasi Web Fase 1

## Ringkasan

Fase 1 memindahkan pengalaman tanya-jawab HGrid247 dari terminal ke interface web berbasis Streamlit. Aplikasi ini adalah workbench RAG untuk membantu pengguna teknis mencari jawaban dari dokumentasi HGrid247-3.5 DE dalam Bahasa Indonesia.

Fokus utama fase ini adalah:

- Menyediakan chat interface yang dapat langsung digunakan melalui browser.
- Menghubungkan interface dengan vector store Qdrant yang sudah berisi dokumen.
- Menggunakan Gemini untuk menyusun jawaban berdasarkan konteks hasil retrieval.
- Menampilkan sumber jawaban agar respons dapat diperiksa kembali.
- Menjaga engine RAG tetap reusable untuk interface terminal, API, dan fase berikutnya.

## Fitur yang Telah Dibuat

### 1. Interface chat berbasis Streamlit

File `app_streamlit.py` menjadi entry point web. Pengguna dapat:

- Membuka aplikasi dari browser melalui `http://localhost:8501`.
- Menulis pertanyaan natural-language tentang HGrid247.
- Mengirim pertanyaan melalui chat composer.
- Melihat riwayat pertanyaan dan jawaban selama session Streamlit berjalan.
- Membaca jawaban dalam format Markdown.

Contoh pertanyaan yang didukung:

- Apa itu HGrid247-3.5 DE?
- Jelaskan alur Source, Assembly, dan Sink.
- Engine atau build target apa saja yang didukung?
- Bagaimana memulai troubleshooting workflow?

### 2. Quick prompts

Sidebar menyediakan beberapa pertanyaan awal yang dapat dipilih dengan satu klik. Quick prompts membantu pengguna memulai eksplorasi dokumentasi tanpa harus mengingat format pertanyaan tertentu.

Sidebar juga menyediakan tombol `Reset percakapan` untuk menghapus riwayat chat pada session aktif.

### 3. Status koneksi dan konfigurasi

Interface menampilkan status operasional sistem, termasuk:

- Status Qdrant.
- Nama collection yang digunakan.
- Model embedding.
- Model Gemini.
- Jumlah top-k retrieval.

Informasi ini membantu membedakan masalah pada interface, vector store, model embedding, atau model generasi.

### 4. Visualisasi alur RAG

Header aplikasi memiliki diagram alur retrieval dengan empat tahap:

1. Pertanyaan pengguna.
2. Retrieval chunk relevan dari Qdrant.
3. Penyusunan jawaban oleh Gemini.
4. Source anchors dari dokumentasi.

Diagram ini bukan sekadar dekorasi. Diagram memperlihatkan model kerja aplikasi: jawaban harus melewati konteks dokumen sebelum ditampilkan kepada pengguna.

### 5. Resolution rail

Setelah pertanyaan dikirim, aplikasi menampilkan status proses dalam resolution rail:

- `Question Load`: pertanyaan diterima.
- `Retrieval Tension`: chunk dokumen sedang dicari dari Qdrant.
- `Answer`: jawaban sedang atau sudah dibuat oleh Gemini.
- `Source Anchors`: jumlah sumber yang berhasil dikumpulkan.

Rail menampilkan jumlah chunk yang digunakan dan jumlah halaman sumber ketika proses selesai.

### 6. Sumber jawaban yang dapat diaudit

Setiap jawaban dapat menampilkan URL sumber dokumen yang dipakai. Sumber diletakkan dekat dengan jawaban agar pengguna dapat:

- Mengetahui dokumen yang mendukung respons.
- Membuka halaman dokumentasi asli.
- Memeriksa jawaban ketika membutuhkan kepastian teknis.

Aplikasi juga menyediakan preview chunk hasil retrieval sebagai konteks tambahan untuk pemeriksaan.

### 7. Tampilan respons error

Jika resource RAG belum siap, aplikasi menampilkan pesan yang mengarahkan pengguna untuk memeriksa:

- Service Qdrant.
- Collection hasil ingest.
- `GOOGLE_API_KEY` pada `.env`.
- Koneksi atau konfigurasi model.

Error tidak disembunyikan sebagai jawaban kosong, sehingga masalah konfigurasi dapat dikenali dari interface.

## Alur Teknis

Alur satu pertanyaan pada Fase 1 adalah:

```text
Pengguna menulis pertanyaan
        |
        v
Streamlit menerima input
        |
        v
Embedding pertanyaan dibuat dengan HuggingFace
        |
        v
Qdrant mengembalikan chunk paling relevan
        |
        v
Chunk digabung menjadi konteks prompt
        |
        v
Gemini menghasilkan jawaban berbasis konteks
        |
        v
Jawaban, jumlah chunk, dan URL sumber ditampilkan
```

Implementasi alur RAG berada di `core/rag.py`, bukan di komponen tampilan. Pemisahan ini membuat fungsi yang sama dapat digunakan oleh `app_streamlit.py` dan `chat.py`.

## Komponen Teknis

### `app_streamlit.py`

Mengatur:

- Konfigurasi halaman Streamlit.
- CSS dan layout interface.
- Sidebar dan quick prompts.
- Riwayat chat melalui `st.session_state`.
- Rendering jawaban, sumber, chunk preview, dan status proses.
- Inisialisasi vector store dan LLM.

### `core/rag.py`

Mengatur:

- Inisialisasi `HuggingFaceEmbeddings`.
- Koneksi `QdrantVectorStore`.
- Inisialisasi `ChatGoogleGenerativeAI`.
- Similarity search dengan nilai `SIMILARITY_TOP_K`.
- Penyusunan prompt berbasis konteks.
- Ekstraksi teks dari respons Gemini.
- Pengumpulan sumber unik dan preview chunk.

Fungsi utama `tanya_hgrid()` mengembalikan data terstruktur:

```python
{
    "jawaban": "...",
    "sumber": ["https://..."],
    "chunks_used": 5,
    "retrieved_chunks": [...],
}
```

### `core/config.py`

Menyediakan konfigurasi dari `.env`, termasuk:

- `QDRANT_URL`
- `QDRANT_COLLECTION`
- `EMBEDDING_MODEL`
- `GEMINI_MODEL`
- `GOOGLE_API_KEY`
- `SIMILARITY_TOP_K`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`

### `core/prompts.py`

Menyimpan prompt yang digunakan untuk jawaban RAG sederhana, RAG dengan memory, dan agent system prompt untuk pengembangan berikutnya.

### `chat.py`

Interface terminal lama tetap tersedia, tetapi sekarang menggunakan engine RAG yang sama dari `core/rag.py`. Perubahan ini mencegah perilaku RAG berbeda antara terminal dan web.

## Arah Desain Interface

Interface sekarang menggunakan konsep `Soft Glass RAG Workbench`: RAG dipresentasikan sebagai command surface glassmorphism yang tetap memperlihatkan composer, status retrieval, jawaban, dan sumber.

Karakter visual yang sudah diterapkan:

- Pale lavender-white canvas untuk area kerja.
- Rounded glass app shell dengan border tipis dan shadow lavender.
- Top navigation compact berisi `Chat`, `Sources`, `Config`, dan `Run`.
- Assistant moment di first viewport dengan teks `Hi, I'm HGrid247 AI`.
- Composer besar berbahan frosted glass dengan primary action violet.
- Quick prompt chips di area utama dan sidebar.
- Cyan-blue sebagai penanda source evidence.
- Glass warning panel untuk error Qdrant, collection, atau `GOOGLE_API_KEY`.
- Layout responsive untuk desktop dan layar kecil tanpa horizontal scroll.

Pendekatan ini menjaga aplikasi terasa seperti alat kerja teknis, bukan landing page atau chatbot generik.

## Data dan Integrasi Fase 1

Fase 1 menggunakan komponen berikut:

- Streamlit sebagai interface web.
- LangChain sebagai orchestration layer.
- HuggingFace sebagai embedding model.
- Qdrant sebagai vector database.
- Gemini sebagai model generasi jawaban.
- Dokumentasi HGrid247 yang sudah di-ingest ke collection `hgrid247_docs`.

Pada implementasi saat ini, collection berisi dokumen hasil ingest dan retrieval mengambil hingga `5` chunk secara default.

## Batasan Fase 1

Fitur berikut belum menjadi bagian dari Fase 1:

- Login dan autentikasi pengguna.
- Multi-user conversation persistence.
- Upload atau ingest dokumen dari browser.
- Pengelolaan collection Qdrant dari interface.
- Streaming token jawaban secara real-time.
- Feedback jawaban, rating, analytics, dan audit log persisten.
- Deployment produksi dan konfigurasi domain.
- Agent dengan tool atau workflow action.

Batasan ini disengaja agar fase awal berfokus pada alur inti: pertanyaan, retrieval, jawaban, dan sumber.

## File yang Ditambahkan atau Diubah

- `app_streamlit.py`: interface web utama.
- `core/__init__.py`: package core.
- `core/config.py`: konfigurasi terpusat.
- `core/prompts.py`: prompt RAG.
- `core/rag.py`: reusable RAG engine.
- `chat.py`: terminal interface yang memakai engine baru.
- `requirements.txt`: dependency Streamlit dan komponen RAG.
- `PRODUCT.md`: product context.
- `DESIGN.md`: design system dan keputusan visual.
- `.impeccable/design.json`: metadata arah desain.

## Status Verifikasi

Fase 1 telah diverifikasi dengan:

- Compile check untuk file Python utama.
- Health check Streamlit yang mengembalikan `ok`.
- Retrieval Qdrant yang berhasil menemukan dokumen relevan.
- End-to-end RAG call dengan Gemini.
- Pengujian desktop dan mobile melalui screenshot review.
- Finish review Impeccable dengan status `ship`.

## Kesimpulan

Web Fase 1 sudah menyediakan fondasi usable untuk HGrid247 AI Assistant: pengguna dapat bertanya melalui browser, sistem mengambil konteks dokumentasi dari Qdrant, Gemini menyusun jawaban, dan sumber respons tetap terlihat untuk verifikasi. Fondasi ini siap dikembangkan ke API, persistence, evaluasi kualitas retrieval, serta agent workflow pada fase berikutnya.
