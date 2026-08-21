"""Adaptador de terminal para o domínio de progresso do BibleLingo.

As regras vivem em ``app.domain.progress``. Este módulo mantém a API histórica
do CLI, incluindo mensagens e persistência JSON, para que a migração aconteça
sem quebrar o usuário atual.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.domain.progress import ActivityResult, Progress as DomainProgress, XpAward


class Progress(DomainProgress):
    """Compatibilidade do CLI sobre o modelo de domínio puro."""

    def add_xp(self, amount: int, reason: str = "") -> bool:
        award: XpAward = super().add_xp(amount, reason)
        if award.amount:
            suffix = f" ({award.reason})" if award.reason else ""
            print(
                f"+{award.amount} XP{suffix} | Total: {award.total_xp} XP | "
                f"Nível {award.level}"
            )
        if award.leveled_up:
            print(f"*** Subiu para o nível {award.level}! ***")
        return award.leveled_up

    def record_activity(self, today=None) -> ActivityResult:
        result = super().record_activity(today=today)
        if result.changed:
            print(
                f"Streak atual: {result.current_streak} dia(s) | "
                f"Recorde: {result.longest_streak}"
            )
        return result

    def save(self, path: str = "progress.json") -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Progresso salvo em {path}")

    def load(self, path: str = "progress.json") -> None:
        file = Path(path)
        if not file.exists():
            print("Nenhum progresso anterior encontrado. Começando do zero.")
            return

        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(
                f"Não foi possível carregar o progresso: {exc}. "
                "Começando do zero."
            )
            return

        self.from_dict(data)
        print(
            f"Progresso carregado: Nível {self.level} | {self.xp} XP | "
            f"Streak {self.current_streak}"
        )


__all__ = ["ActivityResult", "Progress", "XpAward"]


if __name__ == "__main__":
    progress = Progress()
    progress.load()
    print("\n--- Simulando atividade ---")
    progress.record_activity()
    bonus = progress.get_streak_bonus()
    progress.add_xp(int(30 * bonus), "leitura de capítulo")
    progress.save()
