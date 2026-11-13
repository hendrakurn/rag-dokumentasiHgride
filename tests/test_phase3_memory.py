from __future__ import annotations

import asyncio
import copy
import unittest

from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

import api
from core.config import MAX_HISTORY_MESSAGES, SIMILARITY_TOP_K
from core.rag import tanya_hgrid_with_memory


class FakeVectorStore:
    def __init__(self) -> None:
        self.queries: list[dict[str, object]] = []

    def similarity_search(self, query: str, k: int) -> list[Document]:
        self.queries.append({"query": query, "k": k})
        return [
            Document(
                page_content="Source adalah operator untuk membaca data di HGrid247.",
                metadata={"source": "https://docs.example/source"},
            )
        ]


def fake_llm(captured_prompts: list[object]) -> RunnableLambda:
    def respond(prompt_value: object) -> AIMessage:
        captured_prompts.append(prompt_value)
        return AIMessage(content="Jawaban dari fake LLM")

    return RunnableLambda(respond)


class RagMemoryTests(unittest.TestCase):
    def test_without_history_still_works(self) -> None:
        store = FakeVectorStore()
        prompts: list[object] = []

        result = tanya_hgrid_with_memory(
            "Apa itu Source?",
            chat_history=[],
            vector_store=store,
            llm=fake_llm(prompts),
        )

        self.assertEqual(result["jawaban"], "Jawaban dari fake LLM")
        self.assertEqual(result["sumber"], ["https://docs.example/source"])
        self.assertEqual(result["chunks_used"], 1)
        self.assertEqual(store.queries[0]["query"], "Apa itu Source?")
        self.assertEqual(store.queries[0]["k"], SIMILARITY_TOP_K)

    def test_follow_up_question_uses_contextual_retrieval_query(self) -> None:
        store = FakeVectorStore()
        prompts: list[object] = []
        history = [
            {"role": "user", "content": "Apa itu Source di HGrid247?"},
            {
                "role": "assistant",
                "content": "Source adalah operator awal untuk membaca data.",
            },
        ]

        tanya_hgrid_with_memory(
            "Bagaimana cara membuatnya?",
            chat_history=history,
            vector_store=store,
            llm=fake_llm(prompts),
        )

        query = str(store.queries[0]["query"])
        self.assertIn("Apa itu Source di HGrid247?", query)
        self.assertIn("Bagaimana cara membuatnya?", query)

        rendered_messages = prompts[0].to_messages()
        rendered_text = "\n".join(message.content for message in rendered_messages)
        self.assertIn("Apa itu Source di HGrid247?", rendered_text)
        self.assertIn("Bagaimana cara membuatnya?", rendered_text)

    def test_history_is_limited_to_latest_messages(self) -> None:
        store = FakeVectorStore()
        prompts: list[object] = []
        history = [
            {"role": "user", "content": f"pesan-{index}"}
            for index in range(MAX_HISTORY_MESSAGES + 3)
        ]

        tanya_hgrid_with_memory(
            "Pertanyaan sekarang",
            chat_history=history,
            vector_store=store,
            llm=fake_llm(prompts),
        )

        history_lines = set(str(store.queries[0]["query"]).splitlines())
        self.assertNotIn("User: pesan-0", history_lines)
        self.assertNotIn("User: pesan-1", history_lines)
        self.assertNotIn("User: pesan-2", history_lines)
        self.assertIn("User: pesan-3", history_lines)
        self.assertIn(f"User: pesan-{MAX_HISTORY_MESSAGES + 2}", history_lines)

    def test_invalid_history_is_ignored_without_mutating_input(self) -> None:
        store = FakeVectorStore()
        prompts: list[object] = []
        history = [
            {"role": "system", "content": "instruksi internal"},
            {"role": "user", "content": ""},
            {"role": "assistant", "content": None},
            {"role": "assistant", "content": "Jawaban sebelumnya"},
            {"content": "tanpa role"},
            "format rusak",
        ]
        original_history = copy.deepcopy(history)

        tanya_hgrid_with_memory(
            "Lanjutannya apa?",
            chat_history=history,
            vector_store=store,
            llm=fake_llm(prompts),
        )

        self.assertEqual(history, original_history)
        query = str(store.queries[0]["query"])
        self.assertIn("Jawaban sebelumnya", query)
        self.assertNotIn("instruksi internal", query)
        self.assertNotIn("tanpa role", query)


class ApiMemoryTests(unittest.TestCase):
    def test_old_chat_endpoint_still_works(self) -> None:
        original = api.tanya_hgrid
        calls: list[str] = []

        def fake_tanya_hgrid(pertanyaan: str, vector_store=None, llm=None):
            calls.append(pertanyaan)
            return {
                "jawaban": "jawaban lama",
                "sumber": ["doc-1"],
                "chunks_used": 1,
                "retrieved_chunks": [],
            }

        api.tanya_hgrid = fake_tanya_hgrid
        try:
            result = asyncio.run(
                api.chat(
                    api.ChatRequest(pertanyaan="Apa itu HGrid247?", session_id="s1")
                )
            )
        finally:
            api.tanya_hgrid = original

        self.assertEqual(calls, ["Apa itu HGrid247?"])
        self.assertEqual(result.jawaban, "jawaban lama")
        self.assertEqual(result.session_id, "s1")

    def test_session_endpoint_passes_chat_history(self) -> None:
        original = api.tanya_hgrid_with_memory
        calls: list[dict[str, object]] = []

        def fake_tanya_hgrid_with_memory(
            pertanyaan: str,
            chat_history: list[dict[str, str]],
            vector_store=None,
            llm=None,
        ):
            calls.append({"pertanyaan": pertanyaan, "chat_history": chat_history})
            return {
                "jawaban": "jawaban memory",
                "sumber": ["doc-memory"],
                "chunks_used": 2,
                "retrieved_chunks": [],
            }

        api.tanya_hgrid_with_memory = fake_tanya_hgrid_with_memory
        try:
            request = api.ChatSessionRequest(
                pertanyaan="Bagaimana cara membuatnya?",
                session_id="user-123",
                chat_history=[
                    api.ChatMessage(
                        role="user",
                        content="Apa itu Source di HGrid247?",
                    ),
                    api.ChatMessage(
                        role="assistant",
                        content="Source adalah sumber data.",
                    ),
                ],
            )
            result = asyncio.run(api.chat_with_memory(request))
        finally:
            api.tanya_hgrid_with_memory = original

        self.assertEqual(result.jawaban, "jawaban memory")
        self.assertEqual(result.session_id, "user-123")
        self.assertEqual(calls[0]["pertanyaan"], "Bagaimana cara membuatnya?")
        self.assertEqual(
            calls[0]["chat_history"],
            [
                {"role": "user", "content": "Apa itu Source di HGrid247?"},
                {"role": "assistant", "content": "Source adalah sumber data."},
            ],
        )


if __name__ == "__main__":
    unittest.main()
