"""Adaptador de terminal para geração e execução de quizzes.

A seleção de traduções, geração de distratores e correção vivem em
``app.domain.quiz``. Este módulo mantém apenas carregamento de arquivo,
prompts, áudio, RTL e compatibilidade com o contrato de dicionários do CLI.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from app.domain.quiz import (
    QuizQuestion,
    answer_question as domain_answer_question,
    check_answer as domain_check_answer,
    generate_quiz as domain_generate_quiz,
    get_translation as domain_get_translation,
)
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
    dictionary: Dict[str, Dict[str, str]],
    native_lang: str = DEFAULT_NATIVE,
) -> Optional[str]:
    """Mantém a função histórica delegando ao domínio sem fallback."""
    return domain_get_translation(word, dictionary, native_lang)


def generate_quiz(
    words: List[str],
    dictionary: Dict[str, Dict[str, str]],
    native_lang: str = DEFAULT_NATIVE,
    limit: int = 5,
    contexts: Mapping[str, str] | None = None,
) -> List[Dict[str, Any]]:
    """Gera o contrato legado de dicionários para o CLI."""
    questions = domain_generate_quiz(
        words,
        dictionary,
        native_lang=native_lang,
        limit=limit,
        contexts=contexts,
    )
    return [question.to_dict() for question in questions]


def check_answer(question: Dict[str, Any], user_answer: str) -> bool:
    """Mantém a API histórica e delega a correção ao domínio."""
    return domain_check_answer(question, user_answer)


def answer_question(question: Dict[str, Any], selected: str) -> Dict[str, Any]:
    """Retorna o resultado estruturado de uma resposta do CLI ou API."""
    return domain_answer_question(question, selected).to_dict()


def _t(text: str, lang: str) -> str:
    """Aplica preparação RTL somente na camada de apresentação."""
    if is_rtl(lang):
        return prepare_rtl(text, lang)
    return text


def _record_review(vocabulary, word: str, correct: bool):
    """Usa a API de domínio e mantém compatibilidade com objetos antigos."""
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


__all__ = [
    "QuizQuestion",
    "answer_question",
    "check_answer",
    "generate_quiz",
    "get_translation",
    "load_dictionary",
    "run_quiz",
]
