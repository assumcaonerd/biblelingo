"""
Gerenciador do vocabulário do usuário.
"""

from datetime import date


class Vocabulary:
    def __init__(self):
        # palavra -> {"origin": "Gênesis 1:3", "added": "2026-08-20", "reviews": 0}
        self.words = {}

    def add_word(self, word: str, verse_ref: str):
        """
        Adiciona uma palavra ao vocabulário do usuário.

        TODO:
        - Normalizar a palavra (minúsculas)
        - Se já existir, só atualizar a referência ou reviews
        - Se for nova, criar a entrada com data de hoje
        """
        pass

    def get_words_for_quiz(self, limit: int = 5) -> list:
        """
        Retorna uma lista de palavras para o quiz.
        Pode priorizar as que têm menos reviews.

        TODO: implementar lógica simples de seleção
        """
        pass

    def mark_reviewed(self, word: str):
        """Aumenta o contador de revisões de uma palavra."""
        pass
