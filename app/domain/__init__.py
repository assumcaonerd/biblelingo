"""Núcleo de regras de negócio independente de interface e persistência."""

from .progress import ActivityResult, Progress, XpAward
from .quiz import AnswerResult, QuizQuestion, answer_question, check_answer, generate_quiz
from .vocabulary import Vocabulary

__all__ = [
    "ActivityResult",
    "AnswerResult",
    "Progress",
    "QuizQuestion",
    "Vocabulary",
    "XpAward",
    "answer_question",
    "check_answer",
    "generate_quiz",
]
