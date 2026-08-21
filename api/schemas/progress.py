"""Schemas de progresso, XP e streak."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class LevelProgress(BaseModel):
    current: int = Field(description="XP total atual")
    level_start: int = Field(description="XP no início do nível atual")
    next_level: int = Field(description="XP necessário para o próximo nível")
    percent: int = Field(ge=0, le=100, description="Percentual dentro do nível atual")


class ProgressResponse(BaseModel):
    xp: int
    level: int
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date] = None
    streak_bonus: float = Field(description="Multiplicador atual de XP pelo streak")
    level_progress: LevelProgress
