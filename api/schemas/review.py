"""Contratos HTTP para revisão e sessões de estudo."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

from .progress import ProgressResponse


class ReviewAnswerRequest(BaseModel):
    question_id: str = Field(min_length=8, max_length=64)
    selected: str = Field(min_length=1, max_length=512)
    idempotency_key: str = Field(min_length=1, max_length=128)


class ReviewAnswerResponse(BaseModel):
    question_id: str
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


class DueWordItem(BaseModel):
    word: str
    origin: str = ""
    context: str = ""
    next_review: Optional[date] = None


class DueReviewsResponse(BaseModel):
    """GET /reviews/due — somente leitura, sem emitir perguntas."""

    count: int
    native_lang: str
    words: List[DueWordItem] = Field(default_factory=list)
    mode: str = "due"


class StudySessionRequest(BaseModel):
    limit: int = Field(default=5, ge=1, le=20)
    native_lang: Optional[str] = Field(default=None, min_length=2, max_length=8)


class DueQuestion(BaseModel):
    """Pergunta pública — nunca inclui correct."""

    question_id: str
    word: str
    options: List[str]
    context: str = ""
    origin: str = ""
    next_review: Optional[date] = None


class StudySessionResponse(BaseModel):
    """POST /study-sessions — emite question_ids (com side effect explícito)."""

    count: int
    native_lang: str
    questions: List[DueQuestion]
    mode: str = "session"
