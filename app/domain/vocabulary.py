"""Regras puras de vocabulário e revisão espaçada."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Iterable


class Vocabulary:
    """Armazena palavras, origem contextual e estado de revisão."""

    REVIEW_INTERVALS = (1, 3, 7, 14, 30)

    def __init__(self, words: dict[str, dict[str, Any]] | None = None):
        self.words: dict[str, dict[str, Any]] = {}
        if words:
            self.from_dict(words)

    @staticmethod
    def normalize_word(word: str) -> str:
        """Normaliza uma palavra para a chave estável do vocabulário."""
        return str(word).lower().strip()

    def add_word(self, word: str, verse_ref: str, context: str = "") -> bool:
        """Adiciona uma palavra e retorna ``True`` somente quando é nova."""
        normalized = self.normalize_word(word)
        if not normalized:
            return False

        if normalized in self.words:
            entry = self.words[normalized]
            entry["origin"] = verse_ref
            if context:
                entry["context"] = context
            return False

        today = date.today().isoformat()
        self.words[normalized] = {
            "origin": verse_ref,
            "context": context,
            "added": today,
            "reviews": 0,
            "correct_reviews": 0,
            "incorrect_reviews": 0,
            "review_streak": 0,
            "last_reviewed": None,
            "next_review": today,
        }
        return True

    def add_words_from_verse(
        self,
        words: Iterable[str],
        chapter: int,
        verse_number: int,
        book: str = "Genesis",
        verse_text: str = "",
    ) -> int:
        """Adiciona as palavras de um versículo e retorna quantas eram novas."""
        verse_ref = f"{book} {chapter}:{verse_number}"
        return sum(
            self.add_word(word, verse_ref, context=verse_text) for word in words
        )

    @staticmethod
    def _date_or_today(value: Any, today: date | None = None) -> date:
        """Converte datas persistidas; valores ausentes vencem no dia informado."""
        fallback = today or date.today()
        if not value:
            return fallback
        try:
            return date.fromisoformat(str(value))
        except ValueError:
            return fallback

    def get_words_for_quiz(
        self,
        limit: int = 5,
        due_only: bool = False,
        today: date | None = None,
    ) -> list[str]:
        """Prioriza revisões vencidas e depois as palavras menos praticadas."""
        if limit <= 0 or not self.words:
            return []

        reference_date = today or date.today()

        def sort_key(word: str):
            entry = self.words[word]
            next_review = self._date_or_today(entry.get("next_review"), reference_date)
            is_due = next_review <= reference_date
            try:
                reviews = int(entry.get("reviews", 0))
            except (TypeError, ValueError):
                reviews = 0
            return (0 if is_due else 1, next_review, reviews, word)

        selected = sorted(self.words, key=sort_key)
        if due_only:
            selected = [
                word
                for word in selected
                if self._date_or_today(
                    self.words[word].get("next_review"), reference_date
                )
                <= reference_date
            ]
        return selected[:limit]

    def get_due_words(self, limit: int = 5, today: date | None = None) -> list[str]:
        """Retorna apenas palavras cuja próxima revisão já venceu."""
        return self.get_words_for_quiz(limit=limit, due_only=True, today=today)

    def record_review(
        self,
        word: str,
        correct: bool,
        today: date | None = None,
    ) -> bool:
        """Registra uma tentativa e calcula a próxima data de revisão."""
        normalized = self.normalize_word(word)
        entry = self.words.get(normalized)
        if not entry:
            return False

        review_date = today or date.today()
        entry["reviews"] = self._safe_int(entry.get("reviews"), 0) + 1
        entry["correct_reviews"] = self._safe_int(
            entry.get("correct_reviews"), entry["reviews"] - 1
        )
        entry["incorrect_reviews"] = self._safe_int(entry.get("incorrect_reviews"))
        entry["review_streak"] = self._safe_int(entry.get("review_streak"))

        if correct:
            entry["correct_reviews"] += 1
            entry["review_streak"] += 1
            interval_index = min(
                entry["review_streak"] - 1,
                len(self.REVIEW_INTERVALS) - 1,
            )
            days = self.REVIEW_INTERVALS[interval_index]
        else:
            entry["incorrect_reviews"] += 1
            entry["review_streak"] = 0
            days = 0

        entry["last_reviewed"] = review_date.isoformat()
        entry["next_review"] = (review_date + timedelta(days=days)).isoformat()
        return True

    def mark_reviewed(self, word: str, today: date | None = None) -> bool:
        """Compatibilidade com a API antiga para registrar um acerto."""
        return self.record_review(word, correct=True, today=today)

    def total_words(self) -> int:
        return len(self.words)

    def to_dict(self) -> dict[str, dict[str, Any]]:
        return self.words

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def from_dict(self, data: dict[str, Any] | None) -> None:
        """Carrega dados antigos e preenche campos novos com valores seguros."""
        self.words = {}
        for raw_word, raw_entry in (data or {}).items():
            normalized = self.normalize_word(raw_word)
            if not normalized or not isinstance(raw_entry, dict):
                continue

            entry = dict(raw_entry)
            entry.setdefault("origin", "Desconhecida")
            entry.setdefault("context", "")
            entry.setdefault("added", date.today().isoformat())
            entry["reviews"] = self._safe_int(entry.get("reviews"))
            entry["correct_reviews"] = self._safe_int(
                entry.get("correct_reviews"), entry["reviews"]
            )
            entry["incorrect_reviews"] = self._safe_int(
                entry.get("incorrect_reviews")
            )
            entry["review_streak"] = self._safe_int(entry.get("review_streak"))
            entry.setdefault("last_reviewed", None)
            entry.setdefault("next_review", date.today().isoformat())
            self.words[normalized] = entry
