"""
Gerador e executor de quizzes a partir do vocabulário.

O quiz trabalha sempre com traduções explicitamente disponíveis no idioma
selecionado. Isso evita que uma pessoa receba, sem aviso, uma resposta em
português ao escolher outro idioma.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.languages import DEFAULT_NATIVE, get_ui, is_rtl
from app.rtl import prepare_rtl


def load_dictionary(path: str = "data/dictionary.json") -> Dict[str, Dict[str, str]]:
    """Carrega o dicionário no formato ``palavra -> idioma -> tradução``."""
    file = Path(path)
    if not file.exists():
        print(f"Dicionário não encontrado em {path}")
        return {}
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Não foi possível ler o dicionário em {path}: {exc}")
        return {}
    return data if isinstance(data, dict) else {}


def get_translation(
    word: str,
    dictionary: Dict,
    native_lang: str = DEFAULT_NATIVE,
) -> Optional[str]:
    """Retorna uma tradução no idioma solicitado, sem fallback silencioso."""
    entry = dictionary.get(word)
    if not isinstance(entry, dict):
        return None
    translation = entry.get(native_lang)
    return str(translation).strip() if translation else None


def _unique_translations(dictionary: Dict[str, Dict[str, str]], native_lang: str) -> List[str]:
    """Lista traduções únicas e não vazias do idioma escolhido."""
    values = {
        str(entry[native_lang]).strip()
        for entry in dictionary.values()
        if isinstance(entry, dict) and entry.get(native_lang)
    }
    return sorted(values, key=str.casefold)


def generate_quiz(
    words: List[str],
    dictionary: Dict[str, Dict[str, str]],
    native_lang: str = DEFAULT_NATIVE,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Gera perguntas de tradução com opções únicas e idioma consistente."""
    if limit <= 0:
        return []

    available = []
    for word in words:
        translation = get_translation(word, dictionary, native_lang)
        if translation:
            available.append((word, translation))

    if not available:
        return []

    selected = available if len(available) <= limit else random.sample(available, limit)
    all_translations = _unique_translations(dictionary, native_lang)
    questions = []

    for word, correct in selected:
        distractors = [translation for translation in all_translations if translation != correct]
        # Com menos de duas opções erradas, não fabricamos "???"; é melhor
        # deixar a pergunta fora do quiz do que ensinar uma opção falsa.
        if len(distractors) < 2:
            continue
        wrong = random.sample(distractors, min(3, len(distractors)))
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
    """Compara respostas ignorando espaços e diferenças de maiúsculas."""
    return user_answer.strip().casefold() == question["correct"].strip().casefold()


def _t(text: str, lang: str) -> str:
    """Aplica preparação RTL se o idioma for RTL."""
    if is_rtl(lang):
        return prepare_rtl(text, lang)
    return text


def _record_review(vocabulary, word: str, correct: bool):
    """Usa a nova API e mantém compatibilidade com objetos antigos em testes."""
    if not vocabulary:
        return
    if hasattr(vocabulary, "record_review"):
        vocabulary.record_review(word, correct=correct)
    elif correct and hasattr(vocabulary, "mark_reviewed"):
        vocabulary.mark_reviewed(word)


def run_quiz(
    questions: List[Dict[str, Any]],
    vocabulary=None,
    enable_audio: bool = True,
    native_lang: str = DEFAULT_NATIVE,
) -> Dict[str, int]:
    """Executa o quiz no terminal e registra cada tentativa de revisão."""
    ui = get_ui(native_lang)

    if not questions:
        print("Nenhuma pergunta disponível para o quiz.")
        return {"correct": 0, "incorrect": 0, "total": 0}

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

    for number, question in enumerate(questions, 1):
        meaning = _t(ui["meaning_of"], native_lang)
        print(f"{number}. {meaning}: **{question['word']}**?")
        context = question.get("context", "").strip()
        if context:
            print(f"   {_t(ui['context'], native_lang)}: {context}")

        if speak_word:
            try:
                prompt = _t(ui["hear_pronunciation"], native_lang)
                hear = input(f"   {prompt}").strip().lower()
                if hear in ("s", "sim", "y", "yes", "ن", "כ"):
                    speak_word(question["word"])
            except (EOFError, KeyboardInterrupt):
                raise
            except Exception:
                print(f"({_t(ui['audio_unavailable'], native_lang)})")

        for index, option in enumerate(question["options"], 1):
            print(f"   {index}. {_t(option, native_lang)}")

        while True:
            try:
                prompt = _t(ui["your_answer"], native_lang)
                choice = input(f"\n{prompt}").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(question["options"]):
                    break
                print("Escolha um número entre as opções exibidas.")
            except ValueError:
                print("Digite apenas o número da opção.")
            except (EOFError, KeyboardInterrupt):
                raise

        selected = question["options"][choice_num - 1]
        is_correct = check_answer(question, selected)
        _record_review(vocabulary, question["word"], is_correct)

        if is_correct:
            print(f"✓ {_t(ui['correct'], native_lang)}\n")
            correct_count += 1
        else:
            correct_display = _t(question["correct"], native_lang)
            print(f"✗ {_t(ui['wrong'], native_lang)}: {correct_display}\n")

    incorrect_count = len(questions) - correct_count
    result_text = _t(ui["result"], native_lang)
    hits_text = _t(ui["hits"], native_lang)
    print(f"{result_text}: {correct_count}/{len(questions)} {hits_text}")
    return {
        "correct": correct_count,
        "incorrect": incorrect_count,
        "total": len(questions),
    }
