from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from langchain_core.documents import Document

import api
from core.feedback import save_feedback
from core.knowledge import build_context_payload, ingest_text_knowledge, search_knowledge


class FakeVectorStoreWithScore:
    def __init__(self) -> None:
        self.queries: list[dict[str, object]] = []

    def similarity_search_with_score(self, query: str, k: int):
        self.queries.append({"query": query, "k": k})
        return [
            (
                Document(
                    page_content="HGrid247 workflow memakai Source, Assembly, dan Sink.",
                    metadata={"source": "https://docs.example/workflow", "page": 1},
                ),
                0.82,
            )
        ]


class FakeVectorStoreForIngest:
    def __init__(self) -> None:
        self.documents: list[Document] = []

    def add_documents(self, documents: list[Document]) -> list[str]:
        self.documents.extend(documents)
        return [str(index) for index, _ in enumerate(documents)]


class KnowledgeServiceTests(unittest.TestCase):
    def test_search_knowledge_returns_raw_chunks_with_score(self) -> None:
        store = FakeVectorStoreWithScore()

        results = search_knowledge(" workflow ", top_k=3, vector_store=store)

        self.assertEqual(store.queries, [{"query": "workflow", "k": 3}])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "https://docs.example/workflow")
        self.assertEqual(results[0]["score"], 0.82)
        self.assertIn("Source, Assembly, dan Sink", results[0]["content"])

    def test_build_context_payload_formats_sources(self) -> None:
        payload = build_context_payload(
            "workflow",
            top_k=1,
            max_chars=1000,
            vector_store=FakeVectorStoreWithScore(),
        )

        self.assertEqual(payload["query"], "workflow")
        self.assertEqual(payload["sources"], ["https://docs.example/workflow"])
        self.assertEqual(payload["chunks_used"], 1)
        self.assertIn("[1] Source: https://docs.example/workflow", payload["context"])

    def test_ingest_text_knowledge_adds_documents_without_recreate(self) -> None:
        store = FakeVectorStoreForIngest()

        result = ingest_text_knowledge(
            title="Catatan Workflow",
            content="Isi knowledge internal HGrid247.",
            source="project-a/manual-note",
            metadata={"project": "project-a"},
            vector_store=store,
        )

        self.assertEqual(result["message"], "Knowledge ingested.")
        self.assertEqual(result["source"], "project-a/manual-note")
        self.assertGreaterEqual(result["chunks_added"], 1)
        self.assertEqual(store.documents[0].metadata["source"], "project-a/manual-note")
        self.assertEqual(store.documents[0].metadata["project"], "project-a")

    def test_save_feedback_appends_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback.jsonl"

            saved_path = save_feedback(
                question="Apa itu HGrid247?",
                answer="Jawaban lama",
                feedback="Kurang lengkap",
                rating=3,
                source="project-a",
                session_id="s1",
                path=path,
            )

            self.assertEqual(saved_path, str(path))
            rows = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 1)
            payload = json.loads(rows[0])
            self.assertEqual(payload["question"], "Apa itu HGrid247?")
            self.assertEqual(payload["rating"], 3)


class KnowledgeApiTests(unittest.TestCase):
    def test_search_endpoint_uses_configured_vector_store(self) -> None:
        original = api.vector_store
        api.vector_store = FakeVectorStoreWithScore()
        try:
            result = asyncio.run(
                api.search_api(api.SearchRequest(query=" workflow ", top_k=1))
            )
        finally:
            api.vector_store = original

        self.assertEqual(result.query, "workflow")
        self.assertEqual(result.count, 1)
        self.assertEqual(result.results[0].source, "https://docs.example/workflow")

    def test_answer_endpoint_reuses_chat_flow(self) -> None:
        original = api.tanya_hgrid
        calls: list[str] = []

        def fake_tanya_hgrid(pertanyaan: str, vector_store=None, llm=None):
            calls.append(pertanyaan)
            return {
                "jawaban": "jawaban answer",
                "sumber": ["doc-answer"],
                "chunks_used": 1,
                "retrieved_chunks": [],
            }

        api.tanya_hgrid = fake_tanya_hgrid
        try:
            result = asyncio.run(
                api.answer(api.ChatRequest(pertanyaan="Apa itu HGrid247?", session_id="s1"))
            )
        finally:
            api.tanya_hgrid = original

        self.assertEqual(calls, ["Apa itu HGrid247?"])
        self.assertEqual(result.jawaban, "jawaban answer")
        self.assertEqual(result.session_id, "s1")

    def test_workflow_draft_endpoint_writes_json(self) -> None:
        original_output_dir = api.DEFAULT_OUTPUT_DIR
        with tempfile.TemporaryDirectory() as tmp:
            api.DEFAULT_OUTPUT_DIR = Path(tmp)
            try:
                result = asyncio.run(
                    api.workflow_draft(
                        api.WorkflowDraftRequest(
                            name="Demo Workflow",
                            source_config={"type": "HfsSource", "path": "/data/in"},
                            assemblies=[{"type": "Filter", "condition": "status='ACTIVE'"}],
                            sink_config={"type": "HfsSink", "path": "/data/out"},
                        )
                    )
                )
            finally:
                api.DEFAULT_OUTPUT_DIR = original_output_dir

            output_path = Path(result.path)
            self.assertTrue(output_path.exists())
            self.assertEqual(result.workflow["name"], "Demo Workflow")

    def test_skills_endpoint_lists_tools(self) -> None:
        result = asyncio.run(api.list_skills())
        skill_names = {skill.name for skill in result.skills}

        self.assertIn("search_docs", skill_names)
        self.assertIn("create_workflow", skill_names)


if __name__ == "__main__":
    unittest.main()
