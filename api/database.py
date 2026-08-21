"""Infraestrutura SQLite compartilhada pela API do BibleLingo."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path


DEFAULT_USER_ID = "default"
DEFAULT_DATABASE_PATH = Path("data/biblelingo.db")


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    native_language TEXT NOT NULL DEFAULT 'pt',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS progress (
    user_id TEXT PRIMARY KEY,
    xp INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    current_streak INTEGER NOT NULL DEFAULT 0,
    longest_streak INTEGER NOT NULL DEFAULT 0,
    last_activity_date TEXT
);

CREATE TABLE IF NOT EXISTS vocabulary (
    user_id TEXT NOT NULL,
    word TEXT NOT NULL,
    origin TEXT NOT NULL DEFAULT 'API',
    context TEXT NOT NULL DEFAULT '',
    added TEXT NOT NULL,
    reviews INTEGER NOT NULL DEFAULT 0,
    correct_reviews INTEGER NOT NULL DEFAULT 0,
    incorrect_reviews INTEGER NOT NULL DEFAULT 0,
    review_streak INTEGER NOT NULL DEFAULT 0,
    last_reviewed TEXT,
    next_review TEXT NOT NULL,
    PRIMARY KEY (user_id, word)
);

CREATE TABLE IF NOT EXISTS review_events (
    user_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    word TEXT NOT NULL,
    selected TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
    xp_awarded INTEGER NOT NULL DEFAULT 0,
    next_review TEXT NOT NULL,
    review_streak INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    PRIMARY KEY (user_id, idempotency_key)
);
"""


def database_path(path: str | Path | None = None) -> Path:
    """Resolve o banco explicitamente ou pela variável de ambiente."""
    if path is not None:
        return Path(path)
    return Path(os.getenv("BIBLELINGO_DB_PATH", str(DEFAULT_DATABASE_PATH)))


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    """Abre uma conexão configurada para uso seguro pela API."""
    resolved = database_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(
        resolved,
        timeout=30,
        isolation_level=None,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def initialize_database(path: str | Path | None = None) -> None:
    """Cria as tabelas caso ainda não existam."""
    with connect(path) as connection:
        connection.executescript(SCHEMA)
