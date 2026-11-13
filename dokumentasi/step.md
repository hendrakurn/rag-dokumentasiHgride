# 1. Buat virtual environment (opsional tapi disarankan)
python -m venv venv

# 2. Aktifkan virtual environment
# Untuk Linux/Mac:
source venv/bin/activate
# Untuk Windows:
# venv\Scripts\activate

# 3. Instal semua library yang dibutuhkan
pip install langchain langchain-google-genai langchain-qdrant qdrant-client sentence-transformers beautifulsoup4


# Untuk Linux/Mac:
export GOOGLE_API_KEY="ISI_API_KEY_GEMINI_ANDA"
# Untuk Windows (Command Prompt):
# set GOOGLE_API_KEY="ISI_API_KEY_GEMINI_ANDA"





docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant





import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

# 1. Tentukan URL Dokumentasi HGrid247
urls = [
    "https://hgridde.labs247.id/dashboard/hgrid247/index.html",
    "https://hgridde.labs247.id/dashboard/hgrid247/guide/hgrid_user_guide.html"
]

print("Sedang mengambil data dari website HGrid247...")
loader = WebBaseLoader(web_paths=urls)
documents = loader.load()

# 2. Pecah Teks (Chunking)
print("Memecah teks menjadi potongan kecil...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700, 
    chunk_overlap=100 
)
docs = text_splitter.split_documents(documents)
print(f"Berhasil membuat {len(docs)} potongan teks.")

# 3. Embedding & Simpan ke Qdrant
print("Menyimpan ke Qdrant (localhost:6333)...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Ini akan membuat koleksi baru atau menimpa yang lama di Qdrant
qdrant = QdrantVectorStore.from_documents(
    docs,
    embeddings,
    url="http://localhost:6333",
    prefer_grpc=False,
    collection_name="hgrid247_docs"
)

print("Selesai! Data dokumentasi HGrid247 sudah masuk ke Qdrant.")









from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import qdrant_client

# 1. Hubungkan kembali ke Qdrant yang sudah ada datanya
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
client = qdrant_client.QdrantClient(url="http://localhost:6333")

qdrant = QdrantVectorStore(
    client=client,
    collection_name="hgrid247_docs",
    embedding=embeddings
)

# 2. Siapkan Model LLM (Gemini)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# 3. Siapkan Template Prompt
template = """
Kamu adalah asisten teknis AI untuk platform HGrid247. 
Gunakan HANYA konteks di bawah ini untuk menjawab pertanyaan.
Jika kamu tidak menemukan jawabannya di dalam konteks, katakan dengan sopan bahwa informasi tersebut tidak ada di dokumentasi.

Konteks Dokumentasi:
{konteks}

Pertanyaan User: {pertanyaan}

Jawaban:
"""
prompt = PromptTemplate.from_template(template)

# 4. Fungsi Utama untuk Tanya Jawab
def tanya_hgrid(pertanyaan):
    # Cari 3 teks paling relevan dari Qdrant
    hasil_pencarian = qdrant.similarity_search(pertanyaan, k=3)
    konteks = "\n\n---\n\n".join([doc.page_content for doc in hasil_pencarian])
    
    # Eksekusi Rantai (LCEL)
    chain = prompt | llm
    jawaban = chain.invoke({"konteks": konteks, "pertanyaan": pertanyaan})
    return jawaban.content

# 5. Looping Terminal agar bisa chatting terus-menerus
print("🤖 Asisten HGrid247 Siap! (Ketik 'keluar' untuk berhenti)")
while True:
    teks_input = input("\nTanya tentang HGrid247: ")
    if teks_input.lower() == 'keluar':
        break
        
    jawaban_ai = tanya_hgrid(teks_input)
    print(f"\nAI: {jawaban_ai}")




docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant










# Cek apakah Qdrant jalan
docker ps | grep qdrant

# Stop Qdrant
docker stop qdrant

# Start lagi Qdrant (tanpa perlu run ulang)
docker start qdrant

# Lihat log Qdrant
docker logs qdrant

# Cek health Qdrant
curl http://localhost:6333/healthz

# Hapus container (data tetap aman di volume)
docker rm qdrant

# Hapus container + data sekaligus
docker rm qdrant && docker volume rm qdrant_storage









python ingest.py





python chat.py


graphify . --code-only



