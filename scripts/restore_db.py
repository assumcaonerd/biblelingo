#!/usr/bin/env python3
"""Restaura um backup SQLite do BibleLingo após verificar sua integridade."""

from __future__ import annotations

import argparse
from pathlib import Path

from api.backup import restore_backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="arquivo de backup a restaurar")
    parser.add_argument(
        "--database",
        type=Path,
        required=True,
        help="caminho explícito do banco de destino",
    )
    args = parser.parse_args()
    result = restore_backup(args.source, args.database)
    print(f"Banco restaurado: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
