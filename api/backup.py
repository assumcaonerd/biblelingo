"""Backup e restauração seguros do banco SQLite do BibleLingo."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from api.database import database_path


def _integrity_check(connection: sqlite3.Connection) -> None:
    result = connection.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        detail = result[0] if result else "resultado vazio"
        raise RuntimeError(f"integrity_check falhou: {detail}")


def _sidecars(path: Path) -> tuple[Path, Path]:
    return Path(f"{path}-wal"), Path(f"{path}-shm")


def create_backup(
    source: str | Path | None = None,
    destination: str | Path | None = None,
) -> Path:
    """Cria um snapshot consistente do banco usando SQLite online backup."""
    source_path = database_path(source).resolve()
    destination_path = Path(destination or f"{source_path}.bak").resolve()
    if source_path == destination_path:
        raise ValueError("origem e destino do backup devem ser diferentes")
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = destination_path.with_name(destination_path.name + ".tmp")
    if temporary_path.exists():
        temporary_path.unlink()

    try:
        with sqlite3.connect(source_path) as source_connection:
            source_connection.execute("PRAGMA busy_timeout = 5000")
            with sqlite3.connect(temporary_path) as destination_connection:
                source_connection.backup(destination_connection)
                _integrity_check(destination_connection)
                destination_connection.commit()
        os.replace(temporary_path, destination_path)
        os.chmod(destination_path, 0o600)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return destination_path


def restore_backup(
    source: str | Path,
    destination: str | Path | None = None,
) -> Path:
    """Restaura um snapshot em arquivo temporário e troca-o atomicamente."""
    source_path = Path(source).resolve()
    destination_path = database_path(destination).resolve()
    if source_path == destination_path:
        raise ValueError("origem e destino da restauração devem ser diferentes")
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = destination_path.with_name(destination_path.name + ".restore.tmp")
    if temporary_path.exists():
        temporary_path.unlink()

    try:
        with sqlite3.connect(source_path) as source_connection:
            _integrity_check(source_connection)
            with sqlite3.connect(temporary_path) as destination_connection:
                source_connection.backup(destination_connection)
                _integrity_check(destination_connection)
                destination_connection.commit()
        os.replace(temporary_path, destination_path)
        for sidecar in _sidecars(destination_path):
            if sidecar.exists():
                sidecar.unlink()
        os.chmod(destination_path, 0o600)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return destination_path
