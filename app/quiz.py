"""
Gerador e executor de quizzes a partir do vocabulário.
Suporta múltiplos idiomas nativos, incluindo RTL (árabe e hebraico).
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.languages import DEFAULT_NATIVE, get_ui, is_rtl
from app.rtl import prepare_rtl


def load_dictionary(path: str = "data/dictionary.json") -> Dict[str, Dict[str, str]]:
    """
    Carrega o dicionário multi-idioma.
    Formato:
    {
      "word": {"pt": "tradução", "es": "traducción", "ar": "...", "he": "..."}
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
    return entry.get(native_lang) or entry.get("pt")


def generate_quiz(
    words: List[str],
    dictionary: Dict[str, Dict[str, str]],
    native_lang: str = DEFAULT_NATIVE,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Gera perguntas de tradução (múltipla escolha)."""
    available = []
    for w in words:
        translation = get_translation(w, dictionary, native_lang)
        if translation:
            available.append((w, translation))

    if not available:
        return []

    selected = available[:limit] if len(available) <= limit else random.sample(available, limit)

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


def _t(text: str, lang: str) -> str:
    """Aplica preparação RTL se o idioma for RTL."""
    if is_rtl(lang):
        return prepare_rtl(text, lang)
    return text


def run_quiz(
    questions: List[Dict[str, Any]],
    vocabulary=None,
    enable_audio: bool = True,
    native_lang: str = DEFAULT_NATIVE,
) -> Dict[str, int]:
    """Executa o quiz no terminal de forma interativa, com suporte RTL."""
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
            print(f"({_t(ui['audio_unavailable'], native_lang)} – {ui['install_audio']})\n")

    title = _t(ui["quiz_title"], native_lang)
    print(f"\n=== {title} ({len(questions)}) ===\n")
    correct_count = 0

    for i, q in enumerate(questions, 1):
        meaning = _t(ui["meaning_of"], native_lang)
        print(f"{i}. {meaning}: **{q['word']}**?")

        if speak_word:
            try:
                prompt = _t(ui["hear_pronunciation"], native_lang)
                hear = input(f"   {prompt}").strip().lower()
                if hear in ("s", "sim", "y", "yes", "ن", "כ"):
                    speak_word(q["word"])
            except Exception:
                pass

        for idx, opt in enumerate(q["options"], 1):
            # Opções em árabe/hebraico precisam de reshape
            display_opt = _t(opt, native_lang)
            print(f"   {idx}. {display_opt}")

        while True:
            try:
                prompt = _t(ui["your_answer"], native_lang)
                choice = input(f"\n{prompt}").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(q["options"]):
                    break
                print("...")
            except ValueError:
                print("...")

        selected = q["options"][choice_num - 1]
        is_correct = check_answer(q, selected)

        if is_correct:
            print(f"✓ {_t(ui['correct'], native_lang)}\n")
            correct_count += 1
            if vocabulary:
                vocabulary.mark_reviewed(q["word"])
        else:
            correct_display = _t(q["correct"], native_lang)
            print(f"✗ {_t(ui['wrong'], native_lang)}: {correct_display}\n")

    result_text = _t(ui["result"], native_lang)
    hits_text = _t(ui["hits"], native_lang)
    print(f"{result_text}: {correct_count}/{len(questions)} {hits_text}")
    return {"correct": correct_count, "total": len(questions)}
