"""Repositório de conteúdo bíblico (arquivos JSON da WEB)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.bible_loader import format_chapter, get_chapter, get_verse_text, load_book


class ContentRepository:
    def __init__(self, data_dir: str | Path = "data"):
        self.data_dir = Path(data_dir)

    def get_chapter(self, book: str, chapter: int) -> dict[str, Any]:
        """Retorna um capítulo no formato esperado pelos schemas."""
        book_data = load_book(book, data_dir=str(self.data_dir))
        verses_raw = get_chapter(book_data, chapter)

        verses = []
        for item in verses_raw:
            verses.append({
                "verse_number": item.get("verseNumber", 0),
                "text": get_verse_text(item),
            })

        return {
            "book": book.lower(),
            "chapter": chapter,
            "verses": verses,
        }

    def list_available_books(self) -> list[str]:
        """Lista livros disponíveis em data/ (sample ou completo)."""
        books = set()
        for path in self.data_dir.glob("*.json"):
            name = path.stem
            if name.endswith("_sample"):
                name = name.replace("_sample", "")
            if name not in ("dictionary",):
                books.add(name)
        return sorted(books)
