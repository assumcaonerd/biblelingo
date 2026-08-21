#!/usr/bin/env python3
"""Cria um backup consistente do banco SQLite do BibleLingo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.backup import create_backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, help="caminho do banco de origem")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="caminho do arquivo de backup a criar",
    )
    args = parser.parse_args()
    result = create_backup(args.database, args.output)
    print(f"Backup criado: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
