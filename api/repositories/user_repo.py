"""Repositório de usuários."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from api.auth import hash_password, verify_password
from api.database import connect, database_path


class UserRepository:
    def __init__(self, path: str | None = None):
        self.path = database_path(path)

    def create(
        self,
        email: str,
        password: str,
        native_language: str = "pt",
    ) -> dict[str, Any]:
        email = email.strip().lower()
        user_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        password_hash = hash_password(password)

        with connect(self.path) as conn:
            conn.execute("BEGIN")
            try:
                existing = conn.execute(
                    "SELECT id FROM users WHERE email = ?",
                    (email,),
                ).fetchone()
                if existing:
                    raise ValueError("Email already registered")

                conn.execute(
                    """
                    INSERT INTO users (id, email, password_hash, native_language, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, email, password_hash, native_language, created_at),
                )
                # Progresso inicial vazio
                conn.execute(
                    """
                    INSERT OR IGNORE INTO progress (user_id, xp, level, current_streak, longest_streak)
                    VALUES (?, 0, 1, 0, 0)
                    """,
                    (user_id,),
                )
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise

        return {
            "id": user_id,
            "email": email,
            "native_language": native_language,
            "created_at": created_at,
        }

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        email = email.strip().lower()
        with connect(self.path) as conn:
            row = conn.execute(
                "SELECT id, email, password_hash, native_language, created_at FROM users WHERE email = ?",
                (email,),
            ).fetchone()

        if not row:
            return None
        if not verify_password(password, row["password_hash"]):
            return None

        return {
            "id": row["id"],
            "email": row["email"],
            "native_language": row["native_language"],
            "created_at": row["created_at"],
        }

    def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        with connect(self.path) as conn:
            row = conn.execute(
                "SELECT id, email, native_language, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if not row:
            return None
        return dict(row)
