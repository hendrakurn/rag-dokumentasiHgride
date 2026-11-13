# Fase 3: Conversational Memory

Fase 3 membuat chatbot memahami pertanyaan lanjutan dari percakapan sebelumnya.
Contoh: setelah user bertanya "Apa itu Source di HGrid247?", user bisa bertanya
"Bagaimana cara membuatnya?" dan sistem memakai riwayat untuk memahami bahwa
"membuatnya" merujuk ke Source.

## Cara Kerja

1. User mengirim pertanyaan baru.
2. Aplikasi mengambil riwayat percakapan sebelumnya.
3. Sistem membersihkan riwayat:
   - hanya role `user` dan `assistant` yang dipakai
   - content kosong diabaikan
   - input asli tidak diubah
4. Sistem hanya memakai `MAX_HISTORY_MESSAGES` pesan terakhir.
5. Riwayat terbatas digabung dengan pertanyaan baru untuk query pencarian Qdrant.
6. Pertanyaan asli tetap dikirim ke Gemini bersama konteks dokumen dan riwayat terbatas.

## Konfigurasi

Default memory adalah 8 pesan terakhir.

```env
MAX_HISTORY_MESSAGES=8
```

Nilai ini bisa diubah di `.env` tanpa mengubah kode.

## Streamlit

Streamlit memakai `st.session_state.messages` sebagai riwayat percakapan.
Saat user mengirim pertanyaan baru, aplikasi mengambil history terlebih dahulu,
baru menambahkan pertanyaan baru ke tampilan. Dengan cara ini, pertanyaan terbaru
tidak masuk dua kali ke prompt.

## API Stateless

Endpoint lama tetap tersedia:

```http
POST /api/chat
```

Endpoint baru untuk memory:

```http
POST /api/chat/session
```

Contoh request:

```json
{
  "pertanyaan": "Bagaimana cara membuatnya?",
  "session_id": "user-123",
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

Pada Fase 3, API belum menyimpan chat history di server. Aplikasi client yang
menyimpan riwayat dan mengirimkannya lagi pada request berikutnya. `session_id`
hanya menjadi identitas sesi.

## Batasan

- Memory hanya memakai beberapa pesan terakhir, bukan seluruh percakapan.
- Belum ada Redis atau database percakapan.
- Kalau percakapan sangat panjang, pesan lama akan keluar dari konteks.
- Ringkasan otomatis untuk pesan lama belum dibuat pada fase ini.
