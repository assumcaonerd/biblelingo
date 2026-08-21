"""Resumo agregado do progresso de aprendizagem."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

from .progress import ProgressResponse


class VocabularyStats(BaseModel):
    total_words: int = Field(ge=0)
    due_words: int = Field(ge=0)
    reviewed_words: int = Field(ge=0, description="Palavras com ao menos uma revisão")
    never_reviewed: int = Field(ge=0)
    total_reviews: int = Field(ge=0)
    correct_reviews: int = Field(ge=0)
    incorrect_reviews: int = Field(ge=0)
    accuracy_rate: float = Field(
        ge=0,
        le=100,
        description="Percentual de acertos sobre total de revisões",
    )


class RecentActivityItem(BaseModel):
    word: str
    is_correct: bool
    xp_awarded: int
    created_at: str


class DashboardResponse(BaseModel):
    progress: ProgressResponse
    vocabulary: VocabularyStats
    recent_activity: List[RecentActivityItem] = Field(default_factory=list)
    daily_goal: int = Field(
        default=5,
        description="Meta diária sugerida de revisões",
    )
    reviews_today: int = Field(ge=0)
    goal_met: bool
    last_activity_date: Optional[date] = None
