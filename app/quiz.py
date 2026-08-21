"""
Gerador e executor de quizzes a partir do vocabulário.
Suporta múltiplos idiomas nativos (pt, es, ...).
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.languages import DEFAULT_NATIVE, get_ui


def load_dictionary(path: str = "data/dictionary.json") -> Dict[str, Dict[str, str]]:
    """
    Carrega o dicionário multi-idioma.
    Formato:
    {
      "word": {"pt": "tradução", "es": "traducción"}
    }
    """
    file = Path(path)
    if not file.exists():
        print(f"Dicionário não encontrado em {path}")
        return {}
    return json.loads(file.read_text(encoding="utf-8"))


def get_translation(word: str, dictionary: Dict, native_lang: str = DEFAULT_NATIVE) -> Optional[str]:
    """Retorna a tradução da palavra no idioma nativo do usuário."""
    entry = dictionary.get(word)
    if not entry:
        return None
    # Tenta o idioma pedido, depois português como fallback
    return entry.get(native_lang) or entry.get("pt")


def generate_quiz(
    words: List[str],
    dictionary: Dict[str, Dict[str, str]],
    native_lang: str = DEFAULT_NATIVE,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Gera perguntas de tradução (múltipla escolha).
    """
    available = []
    for w in words:
        translation = get_translation(w, dictionary, native_lang)
        if translation:
            available.append((w, translation))

    if not available:
        return []

    selected = available[:limit] if len(available) <= limit else random.sample(available, limit)

    # Todas as traduções possíveis no idioma atual (para distratores)
    all_translations = []
    for entry in dictionary.values():
        t = entry.get(native_lang) or entry.get("pt")
        if t:
            all_translations.append(t)

    questions = []
    for word, correct in selected:
        distractors = [t for t in all_translations if t != correct]
        if len(distractors) >= 3:
            wrong = random.sample(distractors, 3)
        else:
            wrong = distractors + ["???"] * (3 - len(distractors))

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
    return user_answer.strip().lower() == question["correct"].strip().lower()


def run_quiz(
    questions: List[Dict[str, Any]],
    vocabulary=None,
    enable_audio: bool = True,
    native_lang: str = DEFAULT_NATIVE,
) -> Dict[str, int]:
    """
    Executa o quiz no terminal de forma interativa.
    """
    ui = get_ui(native_lang)

    if not questions:
        print("Nenhuma pergunta disponível para o quiz.")
        return {"correct": 0, "total": 0}

    speak_word = None
    if enable_audio:
        try:
            from app.audio import speak_word as _speak
            speak_word = _speak
        except Exception:
            print(f"({ui['audio_unavailable']} – {ui['install_audio']})\n")

    print(f"\n=== {ui['quiz_title']} ({len(questions)} perguntas) ===\n")
    correct_count = 0

    for i, q in enumerate(questions, 1):
        print(f"{i}. {ui['meaning_of']}: **{q['word']}**?")

        if speak_word:
            try:
                hear = input(f"   {ui['hear_pronunciation']}").strip().lower()
                if hear in ("s", "sim", "y", "yes"):
                    speak_word(q["word"])
            except Exception:
                pass

        for idx, opt in enumerate(q["options"], 1):
            print(f"   {idx}. {opt}")

        while True:
            try:
                choice = input(f"\n{ui['your_answer']}").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(q["options"]):
                    break
                print("...")
            except ValueError:
                print("...")

        selected = q["options"][choice_num - 1]
        is_correct = check_answer(q, selected)

        if is_correct:
            print(f"✓ {ui['correct']}\n")
            correct_count += 1
            if vocabulary:
                vocabulary.mark_reviewed(q["word"])
        else:
            print(f"✗ {ui['wrong']}: {q['correct']}\n")

    print(f"{ui['result']}: {correct_count}/{len(questions)} {ui['hits']}")
    return {"correct": correct_count, "total": len(questions)}
