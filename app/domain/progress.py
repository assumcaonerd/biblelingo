"""Regras puras de progresso do BibleLingo.

Este módulo não conhece terminal, JSON, arquivos ou framework web. Ele mantém
apenas o estado e retorna resultados estruturados para cada mutação. Adaptadores
como ``app.progress`` podem decidir como persistir ou exibir esses resultados.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any


@dataclass(frozen=True)
class XpAward:
    """Resultado de uma concessão de XP."""

    amount: int
    reason: str
    total_xp: int
    level: int
    previous_level: int
    leveled_up: bool


@dataclass(frozen=True)
class ActivityResult:
    """Resultado de uma atividade diária."""

    changed: bool
    activity_date: date
    current_streak: int
    longest_streak: int


class Progress:
    """Estado e regras de XP, níveis e sequência diária."""

    def __init__(self):
        self.xp = 0
        self.level = 1
        self.current_streak = 0
        self.longest_streak = 0
        self.last_activity_date: date | None = None
        # Mantido por compatibilidade com o JSON antigo.
        self.vocabulary: dict[str, Any] = {}

    def xp_for_level(self, level: int) -> int:
        """Retorna o XP total necessário para alcançar ``level``."""
        if level <= 1:
            return 0
        return int(50 * (level**1.8))

    def xp_for_next_level(self) -> int:
        """Retorna o XP total necessário para alcançar o próximo nível."""
        return self.xp_for_level(self.level + 1)

    def level_progress(self) -> dict[str, int]:
        """Retorna XP atual, limites do nível e percentual entre 0 e 100."""
        current_goal = self.xp_for_level(self.level)
        next_goal = self.xp_for_next_level()
        span = max(next_goal - current_goal, 1)
        progress = max(0, min(self.xp - current_goal, span))
        return {
            "current": self.xp,
            "level_start": current_goal,
            "next_level": next_goal,
            "percent": int(progress / span * 100),
        }

    def add_xp(self, amount: int, reason: str = "") -> XpAward:
        """Adiciona XP e retorna um evento serializável, sem imprimir nada."""
        amount = max(0, int(amount))
        previous_level = self.level
        if amount:
            self.xp += amount
            while self.xp >= self.xp_for_level(self.level + 1):
                self.level += 1

        return XpAward(
            amount=amount,
            reason=reason,
            total_xp=self.xp,
            level=self.level,
            previous_level=previous_level,
            leveled_up=self.level > previous_level,
        )

    def record_activity(self, today: date | None = None) -> ActivityResult:
        """Registra uma atividade em uma data explícita ou no dia atual."""
        activity_date = today or date.today()

        if self.last_activity_date is None:
            self.current_streak = 1
        elif self.last_activity_date == activity_date:
            return ActivityResult(
                changed=False,
                activity_date=activity_date,
                current_streak=self.current_streak,
                longest_streak=self.longest_streak,
            )
        elif self.last_activity_date == activity_date - timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1

        self.last_activity_date = activity_date
        self.longest_streak = max(self.longest_streak, self.current_streak)
        return ActivityResult(
            changed=True,
            activity_date=activity_date,
            current_streak=self.current_streak,
            longest_streak=self.longest_streak,
        )

    def get_streak_bonus(self) -> float:
        """Retorna o multiplicador de XP da sequência atual."""
        if self.current_streak >= 30:
            return 1.5
        if self.current_streak >= 7:
            return 1.2
        return 1.0

    def to_dict(self) -> dict[str, Any]:
        """Converte o estado para uma estrutura JSON-serializável."""
        return {
            "xp": self.xp,
            "level": self.level,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_activity_date": self.last_activity_date.isoformat()
            if self.last_activity_date
            else None,
            "vocabulary": self.vocabulary,
        }

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def from_dict(self, data: dict[str, Any] | None) -> None:
        """Carrega um estado já decodificado, tolerando JSON antigo ou manual."""
        data = data or {}
        self.xp = max(0, self._safe_int(data.get("xp")))
        self.level = max(1, self._safe_int(data.get("level"), 1))
        self.current_streak = max(0, self._safe_int(data.get("current_streak")))
        self.longest_streak = max(
            self.current_streak,
            self._safe_int(data.get("longest_streak")),
        )

        last = data.get("last_activity_date")
        try:
            self.last_activity_date = date.fromisoformat(str(last)) if last else None
        except ValueError:
            self.last_activity_date = None

        # Corrige arquivos em que o XP total e o nível persistido divergiram.
        while self.xp >= self.xp_for_level(self.level + 1):
            self.level += 1

        vocabulary = data.get("vocabulary", {})
        self.vocabulary = vocabulary if isinstance(vocabulary, dict) else {}
