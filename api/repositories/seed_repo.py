"""Seed idempotente de vocabulário a partir de um capítulo."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.bible_loader import get_chapter, get_verse_text, load_book
from app.domain.quiz import get_translation
from app.parser import extract_words
from app.quiz import load_dictionary

from api.database import DEFAULT_USER_ID
from .progress_repo import ProgressRepository
from .vocabulary_repo import VocabularyRepository


class SeedInputError(ValueError):
    """Capítulo ou livro inválido."""


class SeedRepository:
    def __init__(self) -> None:
        self.progress_repo = ProgressRepository()
        self.vocabulary_repo = VocabularyRepository()

    def seed_chapter(
        self,
        *,
        user_id: str = DEFAULT_USER_ID,
        book: str,
        chapter: int,
        words: list[str] | None = None,
        native_lang: str = "pt",
        today: date | None = None,
    ) -> dict[str, Any]:
        book_key = book.strip().lower()
        if not book_key:
            raise SeedInputError("book must not be empty")
        if chapter < 1:
            raise SeedInputError("chapter must be >= 1")

        try:
            book_data = load_book(book_key)
        except FileNotFoundError as exc:
            raise SeedInputError(str(exc)) from exc

        verses = get_chapter(book_data, chapter)
        if not verses:
            raise SeedInputError(f"No verses found for {book_key} chapter {chapter}")

        book_title = book_key.capitalize()
        dictionary = load_dictionary()
        review_date = today or date.today()

        # Mapa palavra -> (origin, context) da primeira ocorrência útil
        discovered: dict[str, tuple[str, str]] = {}

        if words:
            for raw in words:
                normalized = str(raw).strip().lower()
                if normalized and normalized not in discovered:
                    discovered[normalized] = (f"{book_title} {chapter}", "")
        else:
            for item in verses:
                verse_num = item.get("verseNumber", 0)
                text = get_verse_text(item)
                origin = f"{book_title} {chapter}:{verse_num}"
                for word in extract_words(text):
                    if word not in discovered:
                        discovered[word] = (origin, text)

        connection = self.progress_repo.transaction()
        try:
            vocabulary = self.vocabulary_repo.load(connection, user_id)
            words_new = 0
            words_existing = 0
            with_translation = 0
            sample_new: list[str] = []

            for word, (origin, context) in discovered.items():
                if get_translation(word, dictionary, native_lang):
                    with_translation += 1

                was_new = vocabulary.add_word(word, origin, context=context)
                if was_new:
                    words_new += 1
                    if len(sample_new) < 8:
                        sample_new.append(word)
                else:
                    words_existing += 1

            self.vocabulary_repo.save(connection, vocabulary, user_id)
            due = vocabulary.get_due_words(limit=100, today=review_date)
            connection.commit()

            return {
                "book": book_key,
                "chapter": chapter,
                "words_seen": len(discovered),
                "words_new": words_new,
                "words_existing": words_existing,
                "words_with_translation": with_translation,
                "due_count": len(due),
                "sample_new": sample_new,
            }
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
