"""Schemas de conteúdo bíblico."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class VerseOut(BaseModel):
    verse_number: int
    text: str


class ChapterOut(BaseModel):
    book: str = Field(description="Nome do livro, ex: genesis")
    chapter: int
    verses: List[VerseOut]
