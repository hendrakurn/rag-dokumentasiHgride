"""Feedback persistence helpers for RAG answer review."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_FEEDBACK_PATH = Path("data/feedback.jsonl")


def save_feedback(
    *,
    question: str,
    feedback: str,
    answer: str | None = None,
    rating: int | None = None,
    source: str | None = None,
    session_id: str | None = None,
    path: Path = DEFAULT_FEEDBACK_PATH,
) -> str:
    """Append feedback as JSONL and return the written path."""
    row: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question.strip(),
        "answer": answer.strip() if isinstance(answer, str) else "",
        "feedback": feedback.strip(),
        "rating": rating,
        "source": source.strip() if isinstance(source, str) else "",
        "session_id": session_id.strip() if isinstance(session_id, str) else "",
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    return str(path)
