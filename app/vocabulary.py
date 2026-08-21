"""Adaptador de terminal para vocabulário e revisão espaçada.

As regras de seleção e agendamento vivem em ``app.domain.vocabulary``. Este
módulo preserva a persistência JSON e a API usada pelo CLI.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.domain.vocabulary import Vocabulary as DomainVocabulary


class Vocabulary(DomainVocabulary):
    """Compatibilidade do CLI sobre o modelo de domínio puro."""

    def save(self, path: str = "vocabulary.json") -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Vocabulário salvo em {path} ({self.total_words()} palavras)")

    def load(self, path: str = "vocabulary.json") -> None:
        file = Path(path)
        if not file.exists():
            print("Nenhum vocabulário anterior encontrado.")
            return

        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Não foi possível carregar o vocabulário: {exc}")
            return

        self.from_dict(data)
        print(f"Vocabulário carregado: {self.total_words()} palavras")


__all__ = ["Vocabulary"]
