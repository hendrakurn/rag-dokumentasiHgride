# Design System: HGrid247 AI Assistant

## Creative North Star

**Soft Glass RAG Workbench**

Interface HGrid247 AI sekarang diarahkan sebagai workbench RAG berbahan glassmorphism: ringan, frosted, dan fokus ke operasi chat dokumentasi. Tampilan mengikuti referensi Omago AI secara material, tetapi tetap mempertahankan fungsi HGrid247: bertanya, melihat status retrieval, membaca jawaban, dan mengaudit sumber.

Ini bukan landing page. Layar pertama tetap usable sebagai chat surface.

## Visual Language

- Pale lavender-white canvas sebagai latar utama.
- Rounded app shell besar dengan border putih tipis dan shadow lavender.
- Frosted top navigation: `Chat`, `Sources`, `Config`, `Run`.
- Center assistant moment: `Hi, I'm HGrid247 AI`.
- Composer besar transparan dengan inner highlight.
- Quick prompt chips berbentuk frosted pill.
- Satu primary action violet untuk submit.
- Source evidence memakai cyan-blue agar berbeda dari primary action.
- Warning memakai amber muted dan tetap menjelaskan recovery.

## CSS Tokens

Token utama berada di `app_streamlit.py`:

- `--canvas`
- `--canvas-deep`
- `--glass`
- `--glass-strong`
- `--glass-border`
- `--text-main`
- `--text-muted`
- `--accent`
- `--accent-strong`
- `--source`
- `--warning`
- `--shadow-soft`

Warna tidak disebar sebagai magic color untuk permukaan utama. Violet dipakai hanya untuk action dan active state; cyan dipakai untuk source anchors.

## Components

Komponen visual yang tersedia:

- `.glass-shell`: shell first viewport untuk nav dan assistant moment.
- `.glass-nav`: top navigation frosted.
- `.glass-panel`: panel umum untuk status, empty, warning, dan rail.
- `.glass-composer`: token kelas untuk composer; implementasi Streamlit juga menargetkan `[data-testid="stForm"]`.
- `.glass-chip`: chip mode dan konteks.
- `.glass-action`: gaya action violet.
- `.source-glass`: panel source evidence.
- `.status-glass`: status dan retrieval rail.

## Layout

Desktop:

- Streamlit page container menjadi rounded app shell.
- Header lama dengan force diagram diganti menjadi top-nav glass.
- Composer dipindahkan ke first viewport, overlap lembut dengan assistant stage.
- Quick prompt chips tampil di area utama, selain tetap ada di sidebar.
- Status Qdrant, collection, model, dan Top-K tampil sebagai compact rail.
- Chat history berada di bawah status.

Mobile:

- Shell mengecil ke radius 18px.
- Nav menjadi single-column dan tidak memaksa horizontal page scroll.
- Composer tetap full width.
- Status grid turun ke 2 kolom lalu 1 kolom di layar sangat kecil.
- Quick chips dan source links tetap wrap.
- Target interaksi minimum sekitar 44px.

## Interaction and Accessibility

- Text area tetap memakai label asli `Pertanyaan HGrid247` dengan `label_visibility="collapsed"`.
- Focus ring visible untuk button, link, dan text area.
- Source links tetap terlihat dan underlined, bukan hanya warna.
- Hover hanya memakai transform kecil dan color/shadow change.
- Tidak ada `transition: all`.
- Ada fallback untuk browser tanpa `backdrop-filter`.
- Ada fallback `prefers-reduced-transparency`.
- Ada fallback `prefers-reduced-motion`.

## Error State

Jika Qdrant, collection, atau Gemini belum siap, UI menampilkan glass warning panel dengan instruksi:

- cek service Qdrant,
- pastikan collection sudah di-ingest,
- cek `GOOGLE_API_KEY` di `.env`.

Detail teknis tetap tersedia di expander.

## Source Evidence

Setiap jawaban assistant tetap menampilkan:

- jumlah chunk terpakai,
- jumlah source pages,
- source anchors visible,
- chunk preview di expander.

Evidence tidak disembunyikan total di balik expander.

## Run

```bash
cd /home/hendra/projects/solusi247/dokProjekLangchain-1
source venv/bin/activate
streamlit run app_streamlit.py
```
