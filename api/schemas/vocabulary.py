"""Schemas de vocabulário e seed por capítulo."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SeedChapterRequest(BaseModel):
    book: str = Field(min_length=1, max_length=64, examples=["genesis"])
    chapter: int = Field(ge=1, le=200)
    words: Optional[List[str]] = Field(
        default=None,
        description="Lista opcional; se omitida, o servidor extrai do texto do capítulo.",
    )


class SeedChapterResponse(BaseModel):
    book: str
    chapter: int
    words_seen: int = Field(description="Total de palavras candidatas processadas")
    words_new: int = Field(description="Palavras adicionadas pela primeira vez")
    words_existing: int = Field(description="Palavras que já estavam no vocabulário")
    words_with_translation: int = Field(
        description="Palavras que têm tradução no dicionário"
    )
    due_count: int = Field(description="Palavras vencidas para revisão após o seed")
    sample_new: List[str] = Field(default_factory=list)
