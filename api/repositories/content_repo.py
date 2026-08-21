"""Repositório de conteúdo bíblico via content_manifest.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.bible_loader import get_chapter, get_verse_text, load_book


class ContentNotFoundError(LookupError):
    """Livro/capítulo fora do manifest."""


class ContentRepository:
    def __init__(self, data_dir: str | Path = "data"):
        self.data_dir = Path(data_dir)
        self.manifest_path = self.data_dir / "content_manifest.json"

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return {"books": []}
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def get_chapter(self, book: str, chapter: int) -> dict[str, Any]:
        book_id = book.lower()
        meta = self._chapter_meta(book_id, chapter)
        if meta is None:
            raise ContentNotFoundError(
                f"Chapter not in content manifest: {book_id} {chapter}"
            )

        book_data = load_book(book_id, data_dir=str(self.data_dir))
        verses_raw = get_chapter(book_data, chapter)

        verses = []
        for item in verses_raw:
            verses.append(
                {
                    "verse_number": item.get("verseNumber", 0),
                    "text": get_verse_text(item),
                }
            )

        return {
            "book": book_id,
            "chapter": chapter,
            "verses": verses,
            "label": meta.get("label") or f"{book_id} {chapter}",
            "complete": bool(meta.get("complete")),
            "verse_range": meta.get("verse_range"),
        }

    def list_available_books(self) -> list[str]:
        manifest = self._load_manifest()
        return sorted({b["id"] for b in manifest.get("books", []) if "id" in b})

    def list_lessons(self) -> list[dict[str, Any]]:
        lessons = []
        for book in self._load_manifest().get("books", []):
            for ch in book.get("chapters", []):
                lessons.append(
                    {
                        "book": book["id"],
                        "chapter": ch["number"],
                        "label": ch.get("label", f"{book['id']} {ch['number']}"),
                        "complete": bool(ch.get("complete", False)),
                        "verse_range": ch.get("verse_range"),
                    }
                )
        return lessons

    def _chapter_meta(self, book_id: str, chapter: int) -> dict[str, Any] | None:
        for book in self._load_manifest().get("books", []):
            if book.get("id") != book_id:
                continue
            for ch in book.get("chapters", []):
                if int(ch.get("number", -1)) == chapter:
                    return ch
        return None
