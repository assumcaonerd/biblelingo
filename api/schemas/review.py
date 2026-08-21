"""Contratos HTTP para sessões de revisão (sem vazar a resposta)."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

from .progress import ProgressResponse


class ReviewAnswerRequest(BaseModel):
    """Resposta a uma pergunta previamente emitida pelo servidor."""

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


class DueQuestion(BaseModel):
    """Pergunta pública: nunca inclui a alternativa correta."""

    question_id: str
    word: str
    options: List[str]
    context: str = ""
    origin: str = ""
    next_review: Optional[date] = None


class DueReviewsResponse(BaseModel):
    count: int
    native_lang: str
    questions: List[DueQuestion]
    mode: str = Field(
        default="due",
        description="Sempre 'due' — apenas palavras vencidas; sem seed implícito",
    )
