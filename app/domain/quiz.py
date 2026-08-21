"""Regras puras de tradução, geração de perguntas e correção de respostas."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


Dictionary = Mapping[str, Mapping[str, str]]


@dataclass(frozen=True)
class QuizQuestion:
    """Pergunta de múltipla escolha pronta para uma interface."""

    word: str
    options: tuple[str, ...]
    correct: str
    type: str = "translate"
    context: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Converte a pergunta para o contrato legado do CLI e da API."""
        return {
            "type": self.type,
            "word": self.word,
            "options": list(self.options),
            "correct": self.correct,
            "context": self.context,
        }


@dataclass(frozen=True)
class AnswerResult:
    """Resultado de uma resposta, sem efeitos colaterais."""

    word: str
    selected: str
    correct_answer: str
    is_correct: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "word": self.word,
            "selected": self.selected,
            "correct_answer": self.correct_answer,
            "is_correct": self.is_correct,
        }


def get_translation(
    word: str,
    dictionary: Dictionary,
    native_lang: str,
) -> str | None:
    """Retorna somente a tradução explícita no idioma solicitado."""
    entry = dictionary.get(word)
    if not isinstance(entry, Mapping):
        return None
    translation = entry.get(native_lang)
    if not translation:
        return None
    return str(translation).strip() or None


def _unique_translations(dictionary: Dictionary, native_lang: str) -> list[str]:
    values = {
        str(entry[native_lang]).strip()
        for entry in dictionary.values()
        if isinstance(entry, Mapping) and entry.get(native_lang)
    }
    return sorted(values, key=str.casefold)


def generate_quiz(
    words: Sequence[str],
    dictionary: Dictionary,
    native_lang: str,
    limit: int = 5,
    rng: Any | None = None,
    contexts: Mapping[str, str] | None = None,
) -> list[QuizQuestion]:
    """Gera perguntas sem fallback de idioma, duplicatas ou placeholders."""
    if limit <= 0:
        return []

    random_source = rng or random
    available: list[tuple[str, str]] = []
    for word in words:
        translation = get_translation(word, dictionary, native_lang)
        if translation:
            available.append((word, translation))

    if not available:
        return []

    selected = (
        available
        if len(available) <= limit
        else random_source.sample(available, limit)
    )
    all_translations = _unique_translations(dictionary, native_lang)
    questions: list[QuizQuestion] = []

    for word, correct in selected:
        distractors = [item for item in all_translations if item != correct]
        if len(distractors) < 2:
            continue

        wrong = random_source.sample(distractors, min(3, len(distractors)))
        options = wrong + [correct]
        random_source.shuffle(options)
        questions.append(
            QuizQuestion(
                word=word,
                options=tuple(options),
                correct=correct,
                context=(contexts or {}).get(word, ""),
            )
        )

    return questions


def check_answer(question: QuizQuestion | Mapping[str, Any], user_answer: str) -> bool:
    """Compara uma resposta ignorando espaços e capitalização."""
    correct = question.correct if isinstance(question, QuizQuestion) else question["correct"]
    return user_answer.strip().casefold() == str(correct).strip().casefold()


def answer_question(
    question: QuizQuestion | Mapping[str, Any],
    selected: str,
) -> AnswerResult:
    """Corrige uma pergunta e devolve os dados necessários para persistência."""
    if isinstance(question, QuizQuestion):
        word = question.word
        correct = question.correct
    else:
        word = str(question["word"])
        correct = str(question["correct"])

    return AnswerResult(
        word=word,
        selected=selected,
        correct_answer=correct,
        is_correct=check_answer(question, selected),
    )
