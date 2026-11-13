"""Terminal chat for HGrid247 AI Assistant."""

from core.rag import tanya_hgrid as run_rag

def tanya_hgrid(pertanyaan: str) -> str:
    """Backward-compatible helper that returns only the answer text."""
    return run_rag(pertanyaan)["jawaban"]


def _print_sources(sources: list[str]) -> None:
    if not sources:
        return

    print("\nSumber dokumentasi:")
    for index, source in enumerate(sources, 1):
        print(f"  {index}. {source}")

if __name__ == "__main__":
    print("HGrid247 AI Assistant siap. Ketik 'keluar' untuk berhenti.\n")

    while True:
        teks_input = input("Tanya tentang HGrid247: ").strip()

        if teks_input.lower().strip() in ["keluar", "exit", "quit"]:
            print("Terima kasih. Sampai jumpa.")
            break

        if not teks_input:
            continue

        print("\nSedang mencari jawaban...\n")
        hasil = run_rag(teks_input)
        print(f"AI: {hasil['jawaban']}")
        _print_sources(hasil["sumber"])
        print("-" * 60)
