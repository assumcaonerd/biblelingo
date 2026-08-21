"""Revisão: due em leitura pura; sessão POST emite question_id."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any

from app.domain.progress import Progress
from app.domain.quiz import generate_quiz
from app.quiz import load_dictionary

from api.database import DEFAULT_USER_ID
from api.schemas.progress import LevelProgress, ProgressResponse
from .progress_repo import ProgressRepository
from .vocabulary_repo import VocabularyRepository

QUESTION_TTL_HOURS = 24


class ReviewInputError(ValueError):
    """Entrada inválida ou pergunta inexistente/expirada."""


class ReviewConflictError(ValueError):
    """Conflito de idempotência (mesma key, outra pergunta)."""


class ReviewRepository:
    def __init__(self, progress_repo: ProgressRepository | None = None):
        self.progress_repo = progress_repo or ProgressRepository()
        self.vocabulary_repo = VocabularyRepository()

    def list_due(
        self,
        *,
        user_id: str = DEFAULT_USER_ID,
        native_lang: str = "pt",
        limit: int = 20,
        today: date | None = None,
    ) -> dict[str, Any]:
        """GET puro: lista palavras vencidas sem gravar study_questions."""
        review_date = today or date.today()
        limit = max(1, min(int(limit), 50))

        connection = self.progress_repo.transaction()
        try:
            vocabulary = self.vocabulary_repo.load(connection, user_id)
            due_words = vocabulary.get_due_words(limit=limit, today=review_date)
            words = []
            for w in due_words:
                entry = vocabulary.words.get(w, {})
                words.append(
                    {
                        "word": w,
                        "origin": str(entry.get("origin") or ""),
                        "context": str(entry.get("context") or ""),
                        "next_review": entry.get("next_review"),
                    }
                )
            connection.rollback()  # leitura — não persiste nada
            return {
                "count": len(words),
                "native_lang": native_lang,
                "words": words,
                "mode": "due",
            }
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def create_session(
        self,
        *,
        user_id: str = DEFAULT_USER_ID,
        native_lang: str = "pt",
        limit: int = 5,
        today: date | None = None,
    ) -> dict[str, Any]:
        """POST: emite perguntas. Reutiliza question_id aberto da mesma palavra."""
        review_date = today or date.today()
        limit = max(1, min(int(limit), 20))
        dictionary = load_dictionary()

        connection = self.progress_repo.transaction()
        try:
            vocabulary = self.vocabulary_repo.load(connection, user_id)
            due_words = vocabulary.get_due_words(limit=limit * 2, today=review_date)

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

            now = datetime.now(timezone.utc)
            expires = (now + timedelta(hours=QUESTION_TTL_HOURS)).isoformat()
            payload: list[dict[str, Any]] = []

            for q in questions:
                # Anti-farming: reutilizar pergunta aberta da mesma palavra
                existing = connection.execute(
                    """
                    SELECT * FROM study_questions
                    WHERE user_id = ? AND word = ? AND answered = 0
                      AND expires_at > ?
                    ORDER BY created_at DESC LIMIT 1
                    """,
                    (user_id, q.word, now.isoformat()),
                ).fetchone()

                if existing is not None:
                    options = json.loads(existing["options_json"])
                    entry = vocabulary.words.get(q.word, {})
                    payload.append(
                        {
                            "question_id": existing["question_id"],
                            "word": q.word,
                            "options": options,
                            "context": existing["context"] or "",
                            "origin": existing["origin"] or "",
                            "next_review": entry.get("next_review"),
                        }
                    )
                    continue

                question_id = f"q_{uuid.uuid4().hex}"
                entry = vocabulary.words.get(q.word, {})
                options = list(q.options)

                connection.execute(
                    """
                    INSERT INTO study_questions (
                        question_id, user_id, word, correct_answer, options_json,
                        context, origin, native_lang, answered, created_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                    """,
                    (
                        question_id,
                        user_id,
                        q.word,
                        q.correct,
                        json.dumps(options, ensure_ascii=False),
                        q.context or "",
                        origins.get(q.word, ""),
                        native_lang,
                        now.isoformat(),
                        expires,
                    ),
                )

                payload.append(
                    {
                        "question_id": question_id,
                        "word": q.word,
                        "options": options,
                        "context": q.context or "",
                        "origin": origins.get(q.word, ""),
                        "next_review": entry.get("next_review"),
                    }
                )

            connection.commit()
            return {
                "count": len(payload),
                "native_lang": native_lang,
                "questions": payload,
                "mode": "session",
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
        question_id: str,
        selected: str,
        idempotency_key: str,
        today: date | None = None,
    ) -> dict[str, Any]:
        review_date = today or date.today()
        qid = str(question_id).strip()
        if not qid:
            raise ReviewInputError("question_id must not be empty")

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
                prev_qid = existing["question_id"] or ""
                if prev_qid and prev_qid != qid:
                    raise ReviewConflictError(
                        "idempotency_key already used for a different question_id"
                    )
                progress = ProgressRepository.from_connection(connection, user_id)
                connection.rollback()
                return self._response_from_row(
                    existing, progress, already_processed=True
                )

            question = connection.execute(
                "SELECT * FROM study_questions WHERE question_id = ?",
                (qid,),
            ).fetchone()
            if question is None:
                raise ReviewInputError("Unknown question_id")
            if question["user_id"] != user_id:
                raise ReviewInputError("question_id does not belong to this user")
            if int(question["answered"]) == 1:
                raise ReviewInputError("question already answered")

            expires_at = datetime.fromisoformat(question["expires_at"])
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires_at:
                raise ReviewInputError("question expired")

            options = json.loads(question["options_json"])
            selected_str = str(selected).strip()
            if selected_str not in options and selected_str.casefold() not in {
                o.casefold() for o in options
            }:
                raise ReviewInputError("selected is not a valid option for this question")

            normalized_word = str(question["word"]).strip().lower()
            correct_answer = str(question["correct_answer"])
            is_correct = selected_str.casefold() == correct_answer.strip().casefold()

            progress = ProgressRepository.from_connection(connection, user_id)
            vocabulary = self.vocabulary_repo.load(connection, user_id)

            if normalized_word not in vocabulary.words:
                raise ReviewInputError(
                    "word is not in vocabulary; seed the chapter before answering"
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

            connection.execute(
                "UPDATE study_questions SET answered = 1 WHERE question_id = ?",
                (qid,),
            )

            created_at = datetime.now(timezone.utc).isoformat()
            connection.execute(
                """
                INSERT INTO review_events (
                    user_id, idempotency_key, word, selected, correct_answer,
                    is_correct, xp_awarded, next_review, review_streak, created_at,
                    question_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    idempotency_key,
                    normalized_word,
                    selected_str,
                    correct_answer,
                    int(is_correct),
                    xp_awarded,
                    entry["next_review"],
                    entry["review_streak"],
                    created_at,
                    qid,
                ),
            )
            connection.commit()
            return {
                "question_id": qid,
                "idempotency_key": idempotency_key,
                "word": normalized_word,
                "selected": selected_str,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "already_processed": False,
                "xp_awarded": xp_awarded,
                "next_review": entry["next_review"],
                "review_streak": entry["review_streak"],
                "progress": self._progress_response(progress),
            }
        except (ReviewInputError, ReviewConflictError):
            connection.rollback()
            raise
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
            "question_id": row["question_id"] or "",
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
