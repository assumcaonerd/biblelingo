"""Schemas de conteúdo bíblico."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class VerseOut(BaseModel):
    verse_number: int
    text: str


class ChapterOut(BaseModel):
    book: str = Field(description="Nome do livro, ex: genesis")
    chapter: int
    verses: List[VerseOut]
    label: Optional[str] = Field(
        default=None,
        description="Rótulo editorial, ex: Gênesis 1:1-10 (amostra)",
    )
    complete: bool = False
    verse_range: Optional[str] = None
