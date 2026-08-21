#!/usr/bin/env python3
"""Restaura um backup SQLite do BibleLingo após verificar sua integridade."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
