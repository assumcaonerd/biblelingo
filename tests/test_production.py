from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.backup import create_backup, restore_backup
from api.config import (
    DEFAULT_DEV_SECRET,
    RuntimeConfig,
    validate_runtime_config,
)
from api.database import connect, initialize_database
from api.main import app


class ProductionSafetyTests(unittest.TestCase):
    def test_production_requires_strong_secret_and_explicit_cors(self):
        with self.assertRaises(RuntimeError):
            validate_runtime_config(
                RuntimeConfig(
                    environment="production",
                    secret_key=DEFAULT_DEV_SECRET,
                    token_expire_hours=72,
                    cors_origins=("https://biblelingo.example",),
                )
            )

        with self.assertRaises(RuntimeError):
            validate_runtime_config(
                RuntimeConfig(
                    environment="production",
                    secret_key="short-secret",
                    token_expire_hours=72,
                    cors_origins=("https://biblelingo.example",),
                )
            )

        with self.assertRaises(RuntimeError):
            validate_runtime_config(
                RuntimeConfig(
                    environment="production",
                    secret_key="x" * 48,
                    token_expire_hours=72,
                    cors_origins=("*",),
                )
            )

        validated = validate_runtime_config(
            RuntimeConfig(
                environment="production",
                secret_key="x" * 48,
                token_expire_hours=72,
                cors_origins=("https://biblelingo.example",),
            )
        )
        self.assertTrue(validated.is_production)

    def test_backup_restore_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.db"
            backup = root / "backups" / "snapshot.sqlite"
            restored = root / "restored.db"

            initialize_database(source)
            with connect(source) as connection:
                connection.execute(
                    "INSERT INTO users (id, email, password_hash, native_language, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        "user-1",
                        "backup@example.com",
                        "hash",
                        "pt",
                        "2026-01-01T00:00:00+00:00",
                    ),
                )

            created = create_backup(source, backup)
            self.assertEqual(created, backup.resolve())
            self.assertEqual(backup.stat().st_mode & 0o777, 0o600)

            restored_path = restore_backup(backup, restored)
            self.assertEqual(restored_path, restored.resolve())
            with sqlite3.connect(restored) as connection:
                row = connection.execute(
                    "SELECT email, native_language FROM users WHERE id = ?",
                    ("user-1",),
                ).fetchone()
                integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]

            self.assertEqual(row, ("backup@example.com", "pt"))
            self.assertEqual(integrity, "ok")

    def test_readiness_is_public_and_reports_ready(self):
        previous_db_path = os.environ.get("BIBLELINGO_DB_PATH")
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.environ["BIBLELINGO_DB_PATH"] = str(Path(temp_dir) / "ready.db")
                initialize_database()
                with TestClient(app) as client:
                    response = client.get("/health/ready")
            finally:
                if previous_db_path is None:
                    os.environ.pop("BIBLELINGO_DB_PATH", None)
                else:
                    os.environ["BIBLELINGO_DB_PATH"] = previous_db_path

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "ready")
