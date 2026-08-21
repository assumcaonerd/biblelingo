"""Contratos HTTP para sessões de revisão."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from .progress import ProgressResponse


class ReviewAnswerRequest(BaseModel):
    word: str = Field(min_length=1, max_length=128)
    selected: str = Field(min_length=1, max_length=512)
    native_lang: str = Field(default="pt", min_length=2, max_length=8)
    idempotency_key: str = Field(min_length=1, max_length=128)


class ReviewAnswerResponse(BaseModel):
    idempotency_key: str
    word: str
    selected: str
    correct_answer: str
    is_correct: bool
    already_processed: bool = False
    xp_awarded: int = Field(ge=0)
    next_review: date
    review_streak: int = Field(ge=0)
    progress: ProgressResponse
