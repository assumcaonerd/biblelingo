"""Repositório SQLite para palavras e estado de revisão."""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

from app.domain.vocabulary import Vocabulary

from api.database import DEFAULT_USER_ID


class VocabularyRepository:
    """Converte linhas SQLite para o contrato ``Vocabulary`` do domínio."""

    FIELDS = (
        "word",
        "origin",
        "context",
        "added",
        "reviews",
        "correct_reviews",
        "incorrect_reviews",
        "review_streak",
        "last_reviewed",
        "next_review",
    )

    def __init__(self, legacy_path: str | Path = "vocabulary.json"):
        self.legacy_path = Path(legacy_path)

    def load(
        self,
        connection: sqlite3.Connection,
        user_id: str = DEFAULT_USER_ID,
        *,
        migrate_legacy: bool = True,
    ) -> Vocabulary:
        rows = connection.execute(
            "SELECT * FROM vocabulary WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        if rows:
            return self._from_rows(rows)

        if not migrate_legacy:
            return Vocabulary()

        vocabulary = self._load_legacy()
        self.save(connection, vocabulary, user_id)
        return vocabulary

    def save(
        self,
        connection: sqlite3.Connection,
        vocabulary: Vocabulary,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        for word, entry in vocabulary.words.items():
            data = self._normalize_entry(word, entry)
            connection.execute(
                """
                INSERT INTO vocabulary (
                    user_id, word, origin, context, added, reviews,
                    correct_reviews, incorrect_reviews, review_streak,
                    last_reviewed, next_review
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, word) DO UPDATE SET
                    origin = excluded.origin,
                    context = excluded.context,
                    added = excluded.added,
                    reviews = excluded.reviews,
                    correct_reviews = excluded.correct_reviews,
                    incorrect_reviews = excluded.incorrect_reviews,
                    review_streak = excluded.review_streak,
                    last_reviewed = excluded.last_reviewed,
                    next_review = excluded.next_review
                """,
                (
                    user_id,
                    word,
                    data["origin"],
                    data["context"],
                    data["added"],
                    data["reviews"],
                    data["correct_reviews"],
                    data["incorrect_reviews"],
                    data["review_streak"],
                    data["last_reviewed"],
                    data["next_review"],
                ),
            )

    def ensure_word(
        self,
        connection: sqlite3.Connection,
        vocabulary: Vocabulary,
        word: str,
        user_id: str = DEFAULT_USER_ID,
    ) -> bool:
        """Garante que a palavra exista; retorna True quando foi criada."""
        normalized = vocabulary.normalize_word(word)
        if normalized not in vocabulary.words:
            vocabulary.add_word(normalized, "API review")
            self.save(connection, vocabulary, user_id)
            return True
        return False

    def _from_rows(self, rows: list[sqlite3.Row]) -> Vocabulary:
        data: dict[str, dict[str, Any]] = {}
        for row in rows:
            data[row["word"]] = {
                field: row[field]
                for field in self.FIELDS
                if field != "word"
            }
        return Vocabulary(data)

    def _load_legacy(self) -> Vocabulary:
        vocabulary = Vocabulary()
        if not self.legacy_path.exists():
            return vocabulary
        try:
            data = json.loads(self.legacy_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                vocabulary.from_dict(data)
        except (json.JSONDecodeError, OSError):
            return Vocabulary()
        return vocabulary

    @staticmethod
    def _normalize_entry(word: str, entry: dict[str, Any]) -> dict[str, Any]:
        today = date.today().isoformat()

        def safe_int(value: Any) -> int:
            try:
                return max(0, int(value))
            except (TypeError, ValueError):
                return 0

        return {
            "word": word,
            "origin": str(entry.get("origin") or "API"),
            "context": str(entry.get("context") or ""),
            "added": str(entry.get("added") or today),
            "reviews": safe_int(entry.get("reviews")),
            "correct_reviews": safe_int(entry.get("correct_reviews")),
            "incorrect_reviews": safe_int(entry.get("incorrect_reviews")),
            "review_streak": safe_int(entry.get("review_streak")),
            "last_reviewed": entry.get("last_reviewed"),
            "next_review": str(entry.get("next_review") or today),
        }
