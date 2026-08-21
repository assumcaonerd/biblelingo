"""
Gerador de quizzes simples a partir do vocabulário.
"""

import random


def generate_quiz(words: list[str], dictionary: dict, limit: int = 5) -> list[dict]:
    """
    Gera uma lista de perguntas.

    Formato de cada pergunta:
    {
        "type": "translate",
        "word": "believe",
        "options": ["acreditar", "correr", "comer", "dormir"],
        "correct": "acreditar"
    }

    TODO:
    - Para cada palavra, buscar a tradução no dictionary
    - Criar 3 opções erradas (pode pegar de outras palavras do dicionário)
    - Embaralhar as opções
    - Retornar a lista de perguntas
    """
    pass


def check_answer(question: dict, user_answer: str) -> bool:
    """Verifica se a resposta do usuário está correta."""
    return user_answer.strip().lower() == question["correct"].strip().lower()
