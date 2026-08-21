"""
Gerador e executor de quizzes a partir do vocabulário.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any


def load_dictionary(path: str = "data/dictionary.json") -> Dict[str, str]:
    """Carrega o dicionário inglês → português."""
    file = Path(path)
    if not file.exists():
        print(f"Dicionário não encontrado em {path}")
        return {}
    return json.loads(file.read_text(encoding="utf-8"))


def generate_quiz(
    words: List[str],
    dictionary: Dict[str, str],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Gera perguntas de tradução (múltipla escolha).

    Cada pergunta tem o formato:
    {
        "type": "translate",
        "word": "created",
        "options": ["criou", "correu", "comeu", "dormiu"],
        "correct": "criou"
    }
    """
    # Filtra só as palavras que existem no dicionário
    available = [w for w in words if w in dictionary]
    if not available:
        return []

    selected = available[:limit] if len(available) <= limit else random.sample(available, limit)

    # Lista de traduções possíveis para gerar distratores
    all_translations = list(dictionary.values())

    questions = []
    for word in selected:
        correct = dictionary[word]

        # Gera 3 opções erradas
        distractors = [t for t in all_translations if t != correct]
        if len(distractors) >= 3:
            wrong = random.sample(distractors, 3)
        else:
            wrong = distractors + ["(outra opção)"] * (3 - len(distractors))

        options = wrong + [correct]
        random.shuffle(options)

        questions.append({
            "type": "translate",
            "word": word,
            "options": options,
            "correct": correct,
        })

    return questions


def check_answer(question: Dict[str, Any], user_answer: str) -> bool:
    """Verifica se a resposta está correta (aceita o texto da opção)."""
    return user_answer.strip().lower() == question["correct"].strip().lower()


def run_quiz(questions: List[Dict[str, Any]], vocabulary=None) -> Dict[str, int]:
    """
    Executa o quiz no terminal de forma interativa.
    Retorna {"correct": X, "total": Y}
    """
    if not questions:
        print("Nenhuma pergunta disponível para o quiz.")
        return {"correct": 0, "total": 0}

    print(f"\n=== Quiz ({len(questions)} perguntas) ===\n")
    correct_count = 0

    for i, q in enumerate(questions, 1):
        print(f"{i}. Qual o significado de: **{q['word']}**?")
        for idx, opt in enumerate(q["options"], 1):
            print(f"   {idx}. {opt}")

        while True:
            try:
                choice = input("\nSua resposta (número): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(q["options"]):
                    break
                print("Escolha um número válido.")
            except ValueError:
                print("Digite apenas o número da opção.")

        selected = q["options"][choice_num - 1]
        is_correct = check_answer(q, selected)

        if is_correct:
            print("✓ Correto!\n")
            correct_count += 1
            if vocabulary:
                vocabulary.mark_reviewed(q["word"])
        else:
            print(f"✗ Errado. A resposta certa é: {q['correct']}\n")

    print(f"Resultado: {correct_count}/{len(questions)} acertos")
    return {"correct": correct_count, "total": len(questions)}
