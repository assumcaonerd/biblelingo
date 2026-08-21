"""Repositório SQLite de progresso com compatibilidade de migração JSON."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.domain.progress import Progress

from api.database import DEFAULT_USER_ID, connect, database_path, initialize_database


class ProgressRepository:
    """Persiste progresso por usuário sem alterar o contrato do domínio."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        legacy_path: str | Path = "progress.json",
    ):
        self.db_path = database_path(db_path)
        self.legacy_path = Path(legacy_path)
        initialize_database(self.db_path)

    def load(self, user_id: str = DEFAULT_USER_ID) -> Progress:
        """Carrega o progresso do SQLite e migra JSON legado quando necessário."""
        with connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM progress WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            if row is None:
                progress = self._load_legacy()
                if progress.to_dict() != Progress().to_dict():
                    self._upsert(connection, user_id, progress)
                return progress
            return self._from_row(row)

    def save(self, progress: Progress, user_id: str = DEFAULT_USER_ID) -> None:
        """Salva o estado atual usando uma transação curta."""
        with connect(self.db_path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._upsert(connection, user_id, progress)
            connection.commit()

    def transaction(self) -> sqlite3.Connection:
        """Abre uma conexão para uma operação atômica entre repositórios."""
        connection = connect(self.db_path)
        connection.execute("BEGIN IMMEDIATE")
        return connection

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Progress:
        progress = Progress()
        progress.from_dict(dict(row))
        return progress

    @staticmethod
    def _upsert(
        connection: sqlite3.Connection,
        user_id: str,
        progress: Progress,
    ) -> None:
        data = progress.to_dict()
        connection.execute(
            """
            INSERT INTO progress (
                user_id, xp, level, current_streak, longest_streak,
                last_activity_date
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                xp = excluded.xp,
                level = excluded.level,
                current_streak = excluded.current_streak,
                longest_streak = excluded.longest_streak,
                last_activity_date = excluded.last_activity_date
            """
            ,
            (
                user_id,
                progress.xp,
                progress.level,
                progress.current_streak,
                progress.longest_streak,
                data["last_activity_date"],
            ),
        )

    def _load_legacy(self) -> Progress:
        progress = Progress()
        if not self.legacy_path.exists():
            return progress
        try:
            data = json.loads(self.legacy_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                progress.from_dict(data)
        except (json.JSONDecodeError, OSError):
            return Progress()
        return progress

    @staticmethod
    def from_connection(
        connection: sqlite3.Connection,
        user_id: str = DEFAULT_USER_ID,
    ) -> Progress:
        row = connection.execute(
            "SELECT * FROM progress WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        progress = Progress()
        if row is not None:
            progress.from_dict(dict(row))
        return progress

    @staticmethod
    def save_connection(
        connection: sqlite3.Connection,
        progress: Progress,
        user_id: str = DEFAULT_USER_ID,
    ) -> None:
        ProgressRepository._upsert(connection, user_id, progress)
