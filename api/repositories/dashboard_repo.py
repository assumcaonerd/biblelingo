"""Agrega progresso, vocabulário e atividade recente para o dashboard."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from api.database import DEFAULT_USER_ID, connect, database_path, initialize_database
from api.schemas.progress import LevelProgress, ProgressResponse
from .progress_repo import ProgressRepository
from .vocabulary_repo import VocabularyRepository


class DashboardRepository:
    def __init__(self, db_path: str | None = None):
        self.db_path = database_path(db_path)
        initialize_database(self.db_path)
        self.progress_repo = ProgressRepository(db_path=self.db_path)
        self.vocabulary_repo = VocabularyRepository()

    def summary(
        self,
        *,
        user_id: str = DEFAULT_USER_ID,
        daily_goal: int = 5,
        recent_limit: int = 8,
        today: date | None = None,
    ) -> dict[str, Any]:
        reference = today or date.today()
        daily_goal = max(1, min(int(daily_goal), 50))

        with connect(self.db_path) as connection:
            progress = ProgressRepository.from_connection(connection, user_id)
            vocabulary = self.vocabulary_repo.load(connection, user_id)

            total_words = vocabulary.total_words()
            due_words = len(vocabulary.get_due_words(limit=10_000, today=reference))
            reviewed_words = 0
            never_reviewed = 0
            total_reviews = 0
            correct_reviews = 0
            incorrect_reviews = 0

            for entry in vocabulary.words.values():
                reviews = _safe_int(entry.get("reviews"))
                correct = _safe_int(entry.get("correct_reviews"))
                incorrect = _safe_int(entry.get("incorrect_reviews"))
                total_reviews += reviews
                correct_reviews += correct
                incorrect_reviews += incorrect
                if reviews > 0:
                    reviewed_words += 1
                else:
                    never_reviewed += 1

            accuracy = (
                round(100.0 * correct_reviews / total_reviews, 1)
                if total_reviews > 0
                else 0.0
            )

            today_prefix = reference.isoformat()
            reviews_today_row = connection.execute(
                """
                SELECT COUNT(*) AS c FROM review_events
                WHERE user_id = ? AND created_at LIKE ?
                """,
                (user_id, f"{today_prefix}%"),
            ).fetchone()
            reviews_today = int(reviews_today_row["c"] if reviews_today_row else 0)

            rows = connection.execute(
                """
                SELECT word, is_correct, xp_awarded, created_at
                FROM review_events
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, max(1, min(recent_limit, 20))),
            ).fetchall()

            recent = [
                {
                    "word": row["word"],
                    "is_correct": bool(row["is_correct"]),
                    "xp_awarded": int(row["xp_awarded"]),
                    "created_at": row["created_at"],
                }
                for row in rows
            ]

        level_progress = progress.level_progress()
        return {
            "progress": ProgressResponse(
                xp=progress.xp,
                level=progress.level,
                current_streak=progress.current_streak,
                longest_streak=progress.longest_streak,
                last_activity_date=progress.last_activity_date,
                streak_bonus=progress.get_streak_bonus(),
                level_progress=LevelProgress(**level_progress),
            ),
            "vocabulary": {
                "total_words": total_words,
                "due_words": due_words,
                "reviewed_words": reviewed_words,
                "never_reviewed": never_reviewed,
                "total_reviews": total_reviews,
                "correct_reviews": correct_reviews,
                "incorrect_reviews": incorrect_reviews,
                "accuracy_rate": accuracy,
            },
            "recent_activity": recent,
            "daily_goal": daily_goal,
            "reviews_today": reviews_today,
            "goal_met": reviews_today >= daily_goal,
            "last_activity_date": progress.last_activity_date,
        }


def _safe_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0
