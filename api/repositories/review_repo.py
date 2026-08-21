"""Operações atômicas de revisão, idempotência e palavras vencidas."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone
from typing import Any

from app.domain.progress import Progress
from app.domain.quiz import generate_quiz, get_translation
from app.quiz import load_dictionary

from api.database import DEFAULT_USER_ID
from api.schemas.progress import LevelProgress, ProgressResponse
from .progress_repo import ProgressRepository
from .vocabulary_repo import VocabularyRepository

# Palavras iniciais de Gênesis 1 para quem ainda não tem vocabulário.
# Cada entrada preserva a referência e o versículo exibido no contexto da pergunta.
STARTER_WORDS = (
    (
        "beginning",
        "Genesis 1:1",
        "In the beginning, God created the heavens and the earth.",
    ),
    (
        "god",
        "Genesis 1:1",
        "In the beginning, God created the heavens and the earth.",
    ),
    (
        "created",
        "Genesis 1:1",
        "In the beginning, God created the heavens and the earth.",
    ),
    (
        "heavens",
        "Genesis 1:1",
        "In the beginning, God created the heavens and the earth.",
    ),
    (
        "earth",
        "Genesis 1:1",
        "In the beginning, God created the heavens and the earth.",
    ),
    (
        "darkness",
        "Genesis 1:2",
        "Darkness was on the surface of the deep.",
    ),
    (
        "light",
        "Genesis 1:3",
        "God said, Let there be light, and there was light.",
    ),
    (
        "waters",
        "Genesis 1:2",
        "God's Spirit was hovering over the surface of the waters.",
    ),
    (
        "spirit",
        "Genesis 1:2",
        "God's Spirit was hovering over the surface of the waters.",
    ),
    (
        "day",
        "Genesis 1:5",
        "God called the light day, and the darkness he called night.",
    ),
    (
        "night",
        "Genesis 1:5",
        "God called the light day, and the darkness he called night.",
    ),
    (
        "good",
        "Genesis 1:4",
        "God saw the light, and saw that it was good.",
    ),
)


class ReviewInputError(ValueError):
    """Indica palavra ou idioma sem tradução disponível."""


class ReviewRepository:
    """Aplica uma resposta de revisão como uma única unidade SQLite."""

    def __init__(self, progress_repo: ProgressRepository | None = None):
        self.progress_repo = progress_repo or ProgressRepository()
        self.vocabulary_repo = VocabularyRepository()

    def list_due(
        self,
        *,
        user_id: str = DEFAULT_USER_ID,
        native_lang: str = "pt",
        limit: int = 5,
        today: date | None = None,
        seed_if_empty: bool = True,
    ) -> dict[str, Any]:
        """Retorna perguntas de palavras vencidas (ou seed inicial)."""
        review_date = today or date.today()
        limit = max(1, min(int(limit), 20))
        dictionary = load_dictionary()

        connection = self.progress_repo.transaction()
        try:
            vocabulary = self.vocabulary_repo.load(connection, user_id)

            if seed_if_empty and vocabulary.total_words() == 0:
                for word, origin, context in STARTER_WORDS:
                    if get_translation(word, dictionary, native_lang):
                        vocabulary.add_word(word, origin, context=context)
                self.vocabulary_repo.save(connection, vocabulary, user_id)
                connection.commit()

            due_words = vocabulary.get_due_words(limit=limit * 2, today=review_date)
            if not due_words:
                # Sem vencidas: usa as menos praticadas para não deixar a sessão vazia.
                due_words = vocabulary.get_words_for_quiz(
                    limit=limit * 2, due_only=False, today=review_date
                )

            contexts = {
                w: str(vocabulary.words.get(w, {}).get("context") or "")
                for w in due_words
            }
            origins = {
                w: str(vocabulary.words.get(w, {}).get("origin") or "")
                for w in due_words
            }

            questions = generate_quiz(
                due_words,
                dictionary,
                native_lang=native_lang,
                limit=limit,
                contexts=contexts,
            )

            payload = []
            for q in questions:
                entry = vocabulary.words.get(q.word, {})
                next_review = entry.get("next_review")
                payload.append(
                    {
                        "word": q.word,
                        "options": list(q.options),
                        "correct": q.correct,
                        "context": q.context,
                        "origin": origins.get(q.word, ""),
                        "next_review": next_review,
                    }
                )

            connection.commit()
            return {
                "count": len(payload),
                "native_lang": native_lang,
                "questions": payload,
            }
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def answer(
        self,
        *,
        user_id: str = DEFAULT_USER_ID,
        word: str,
        selected: str,
        native_lang: str,
        idempotency_key: str,
        today: date | None = None,
    ) -> dict[str, Any]:
        review_date = today or date.today()
        normalized_word = str(word).strip().lower()
        if not normalized_word:
            raise ReviewInputError("word must not be empty")

        dictionary = load_dictionary()
        correct_answer = get_translation(normalized_word, dictionary, native_lang)
        if correct_answer is None:
            raise ReviewInputError(
                f"No translation available for '{normalized_word}' in '{native_lang}'"
            )

        connection = self.progress_repo.transaction()
        try:
            existing = connection.execute(
                """
                SELECT * FROM review_events
                WHERE user_id = ? AND idempotency_key = ?
                """,
                (user_id, idempotency_key),
            ).fetchone()
            if existing is not None:
                progress = ProgressRepository.from_connection(connection, user_id)
                connection.rollback()
                return self._response_from_row(
                    existing,
                    progress,
                    already_processed=True,
                )

            progress = ProgressRepository.from_connection(connection, user_id)
            vocabulary = self.vocabulary_repo.load(connection, user_id)
            self.vocabulary_repo.ensure_word(
                connection,
                vocabulary,
                normalized_word,
                user_id,
            )

            is_correct = (
                str(selected).strip().casefold()
                == correct_answer.strip().casefold()
            )
            progress.record_activity(today=review_date)
            bonus = progress.get_streak_bonus()
            xp_awarded = int(10 * bonus) if is_correct else 0
            progress.add_xp(
                xp_awarded,
                "resposta correta" if is_correct else "resposta revisada",
            )
            vocabulary.record_review(
                normalized_word,
                correct=is_correct,
                today=review_date,
            )
            entry = vocabulary.words[normalized_word]

            ProgressRepository.save_connection(connection, progress, user_id)
            self.vocabulary_repo.save(connection, vocabulary, user_id)
            created_at = datetime.now(timezone.utc).isoformat()
            connection.execute(
                """
                INSERT INTO review_events (
                    user_id, idempotency_key, word, selected, correct_answer,
                    is_correct, xp_awarded, next_review, review_streak, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    idempotency_key,
                    normalized_word,
                    str(selected),
                    correct_answer,
                    int(is_correct),
                    xp_awarded,
                    entry["next_review"],
                    entry["review_streak"],
                    created_at,
                ),
            )
            connection.commit()
            return {
                "idempotency_key": idempotency_key,
                "word": normalized_word,
                "selected": str(selected),
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "already_processed": False,
                "xp_awarded": xp_awarded,
                "next_review": entry["next_review"],
                "review_streak": entry["review_streak"],
                "progress": self._progress_response(progress),
            }
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _progress_response(progress: Progress) -> ProgressResponse:
        level_progress = progress.level_progress()
        return ProgressResponse(
            xp=progress.xp,
            level=progress.level,
            current_streak=progress.current_streak,
            longest_streak=progress.longest_streak,
            last_activity_date=progress.last_activity_date,
            streak_bonus=progress.get_streak_bonus(),
            level_progress=LevelProgress(**level_progress),
        )

    def _response_from_row(
        self,
        row: sqlite3.Row,
        progress: Progress,
        *,
        already_processed: bool,
    ) -> dict[str, Any]:
        return {
            "idempotency_key": row["idempotency_key"],
            "word": row["word"],
            "selected": row["selected"],
            "correct_answer": row["correct_answer"],
            "is_correct": bool(row["is_correct"]),
            "already_processed": already_processed,
            "xp_awarded": row["xp_awarded"],
            "next_review": row["next_review"],
            "review_streak": row["review_streak"],
            "progress": self._progress_response(progress),
        }
