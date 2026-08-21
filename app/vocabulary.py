"""
Gerenciador do vocabulário do usuário.
Guarda palavras aprendidas a partir da leitura da Bíblia.
"""

from datetime import date
from typing import List, Dict, Any
import json
from pathlib import Path


class Vocabulary:
    def __init__(self):
        # palavra -> {"origin": "Genesis 1:3", "added": "2026-08-20", "reviews": 0}
        self.words: Dict[str, Dict[str, Any]] = {}

    def add_word(self, word: str, verse_ref: str) -> bool:
        """
        Adiciona uma palavra ao vocabulário.
        Retorna True se a palavra era nova, False se já existia.
        """
        word = word.lower().strip()
        if not word:
            return False

        if word in self.words:
            # Já existe: só atualiza a referência de origem se quiser
            self.words[word]["origin"] = verse_ref
            return False

        self.words[word] = {
            "origin": verse_ref,
            "added": date.today().isoformat(),
            "reviews": 0,
        }
        return True

    def add_words_from_verse(self, words: List[str], chapter: int, verse_number: int, book: str = "Genesis") -> int:
        """
        Adiciona várias palavras de um mesmo versículo.
        Retorna quantas palavras novas foram adicionadas.
        """
        ref = f"{book} {chapter}:{verse_number}"
        new_count = 0
        for word in words:
            if self.add_word(word, ref):
                new_count += 1
        return new_count

    def get_words_for_quiz(self, limit: int = 5) -> List[str]:
        """
        Retorna palavras priorizando as que têm menos revisões.
        """
        if not self.words:
            return []

        # Ordena por número de reviews (menos revisadas primeiro)
        sorted_words = sorted(
            self.words.keys(),
            key=lambda w: self.words[w]["reviews"]
        )
        return sorted_words[:limit]

    def mark_reviewed(self, word: str):
        """Aumenta o contador de revisões de uma palavra."""
        word = word.lower().strip()
        if word in self.words:
            self.words[word]["reviews"] += 1

    def total_words(self) -> int:
        return len(self.words)

    def to_dict(self) -> dict:
        return self.words

    def from_dict(self, data: dict):
        self.words = data if data else {}

    def save(self, path: str = "vocabulary.json"):
        Path(path).write_text(
            json.dumps(self.words, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"Vocabulário salvo em {path} ({self.total_words()} palavras)")

    def load(self, path: str = "vocabulary.json"):
        file = Path(path)
        if not file.exists():
            print("Nenhum vocabulário anterior encontrado.")
            return
        data = json.loads(file.read_text(encoding="utf-8"))
        self.from_dict(data)
        print(f"Vocabulário carregado: {self.total_words()} palavras")
