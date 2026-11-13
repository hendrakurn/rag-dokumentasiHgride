"""Tools untuk interaksi dengan HGrid247 system."""
from langchain_core.tools import tool
from core.rag import get_vector_store, extract_text_from_response


@tool
def search_docs(query: str) -> str:
    """
    Cari informasi di dokumentasi HGrid247-3.5 DE.
    Gunakan tool ini untuk menjawab pertanyaan tentang fitur,
    cara penggunaan, konfigurasi, dan troubleshooting HGrid247.
    
    Args:
        query: Pertanyaan atau keyword pencarian
    
    Returns:
        Konteks dokumentasi yang relevan
    """
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=5)
    if not results:
        return "Tidak ditemukan informasi relevan di dokumentasi."
    
    output = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "Unknown")
        output.append(f"[{i}] (Sumber: {source})\n{doc.page_content}")
    
    return "\n\n---\n\n".join(output)


@tool
def list_engines() -> str:
    """
    Daftar semua engine/build target yang didukung HGrid247.
    
    Returns:
        Daftar engine beserta output file-nya
    """
    engines = {
        "MapReduce": "<project>_mr.jar",
        "Spark 1.6 RDD": "<project>_spark1.jar",
        "Spark 2.x RDD": "<project>_spark2.jar",
        "Spark 2.x Dataset": "<project>_spark2ds.jar",
        "Beam 2.29.0 (Batch)": "<project>_beam.jar",
        "Beam 2.29.0 (Streaming)": "<project>_sbeam.jar",
        "Flink 1.12.x (Batch)": "<project>_flink.jar",
        "Flink 1.12.x (Streaming)": "<project>_sflink.jar",
        "Tez 0.9.1": "<project>_tez.jar",
        "PySpark": "<flow-name>.py",
    }
    lines = ["Engine HGrid247 yang Tersedia:", ""]
    for engine, output in engines.items():
        lines.append(f"  • {engine} → Output: {output}")
    return "\n".join(lines)
