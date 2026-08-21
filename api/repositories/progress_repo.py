"""Repositório de progresso (JSON local por enquanto).

Na próxima fase isso vira SQLite/PostgreSQL sem alterar as rotas.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.domain.progress import Progress


class ProgressRepository:
    def __init__(self, path: str | Path = "progress.json"):
        self.path = Path(path)

    def load(self) -> Progress:
        progress = Progress()
        if not self.path.exists():
            return progress
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            progress.from_dict(data)
        except (json.JSONDecodeError, OSError):
            pass
        return progress

    def save(self, progress: Progress) -> None:
        self.path.write_text(
            json.dumps(progress.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
