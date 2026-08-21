"""
Gerenciador do vocabulário do usuário.

Além de guardar a origem de cada palavra, o módulo mantém um agendamento
local e simples de revisão espaçada. O formato continua compatível com o
JSON antigo: campos novos são adicionados apenas quando uma palavra é revisada.
"""

from datetime import date, timedelta
from typing import List, Dict, Any
import json
from pathlib import Path


class Vocabulary:
    """Armazena palavras aprendidas e o histórico de revisões."""

    # Intervalos progressivos para respostas corretas. Uma resposta errada
    # retorna a palavra para revisão no mesmo dia.
    REVIEW_INTERVALS = (1, 3, 7, 14, 30)

    def __init__(self):
        # palavra -> metadados de origem, revisões e próximo vencimento
        self.words: Dict[str, Dict[str, Any]] = {}

    def add_word(self, word: str, verse_ref: str, context: str = "") -> bool:
        """
        Adiciona uma palavra ao vocabulário.

        Retorna ``True`` quando a palavra era nova. Quando ela já existe, a
        origem mais recente é preservada sem apagar o histórico de revisão.
        """
        word = word.lower().strip()
        if not word:
            return False

        if word in self.words:
            self.words[word]["origin"] = verse_ref
            if context:
                self.words[word]["context"] = context
            return False

        self.words[word] = {
            "origin": verse_ref,
            "context": context,
            "added": date.today().isoformat(),
            "reviews": 0,
            "correct_reviews": 0,
            "incorrect_reviews": 0,
            "review_streak": 0,
            "last_reviewed": None,
            # Palavra nova está imediatamente disponível para estudo.
            "next_review": date.today().isoformat(),
        }
        return True

    def add_words_from_verse(
        self,
        words: List[str],
        chapter: int,
        verse_number: int,
        book: str = "Genesis",
        verse_text: str = "",
    ) -> int:
        """Adiciona várias palavras de um versículo e retorna as novas."""
        ref = f"{book} {chapter}:{verse_number}"
        new_count = 0
        for word in words:
            if self.add_word(word, ref, context=verse_text):
                new_count += 1
        return new_count

    @staticmethod
    def _date_or_today(value: Any) -> date:
        """Converte uma data persistida; dados antigos/invalidos vencem hoje."""
        if not value:
            return date.today()
        try:
            return date.fromisoformat(str(value))
        except ValueError:
            return date.today()

    def get_words_for_quiz(self, limit: int = 5, due_only: bool = False) -> List[str]:
        """
        Retorna palavras priorizando as revisões vencidas e menos praticadas.

        Palavras sem ``next_review`` são tratadas como vencidas, o que permite
        que vocabulários criados por versões antigas continuem funcionando.
        """
        if limit <= 0 or not self.words:
            return []

        today = date.today()

        def sort_key(word: str):
            entry = self.words[word]
            next_review = self._date_or_today(entry.get("next_review"))
            is_due = next_review <= today
            # Vencidas primeiro; entre elas, menor data e menos revisões.
            return (
                0 if is_due else 1,
                next_review,
                int(entry.get("reviews", 0)),
                word,
            )

        selected = sorted(self.words, key=sort_key)
        if due_only:
            selected = [
                word
                for word in selected
                if self._date_or_today(self.words[word].get("next_review")) <= today
            ]
        return selected[:limit]

    def get_due_words(self, limit: int = 5) -> List[str]:
        """Atalho explícito para montar uma sessão apenas com palavras vencidas."""
        return self.get_words_for_quiz(limit=limit, due_only=True)

    def record_review(self, word: str, correct: bool) -> bool:
        """
        Registra uma tentativa e agenda a próxima revisão.

        Respostas corretas avançam por intervalos de 1, 3, 7, 14 e 30 dias.
        Uma resposta errada zera a sequência e torna a palavra disponível hoje.
        Retorna ``True`` se a palavra existir no vocabulário.
        """
        word = word.lower().strip()
        entry = self.words.get(word)
        if not entry:
            return False

        today = date.today()
        entry["reviews"] = int(entry.get("reviews", 0)) + 1
        entry.setdefault("correct_reviews", 0)
        entry.setdefault("incorrect_reviews", 0)
        entry.setdefault("review_streak", 0)

        if correct:
            entry["correct_reviews"] += 1
            entry["review_streak"] += 1
            interval_index = min(entry["review_streak"] - 1, len(self.REVIEW_INTERVALS) - 1)
            days = self.REVIEW_INTERVALS[interval_index]
        else:
            entry["incorrect_reviews"] += 1
            entry["review_streak"] = 0
            days = 0

        entry["last_reviewed"] = today.isoformat()
        entry["next_review"] = (today + timedelta(days=days)).isoformat()
        return True

    def mark_reviewed(self, word: str):
        """Compatibilidade com a API antiga: registra uma resposta correta."""
        self.record_review(word, correct=True)

    def total_words(self) -> int:
        return len(self.words)

    def to_dict(self) -> dict:
        return self.words

    def from_dict(self, data: dict):
        """Carrega dados antigos e preenche campos novos sem perder histórico."""
        self.words = {}
        for raw_word, raw_entry in (data or {}).items():
            word = str(raw_word).lower().strip()
            if not word or not isinstance(raw_entry, dict):
                continue
            entry = dict(raw_entry)
            entry.setdefault("origin", "Desconhecida")
            entry.setdefault("context", "")
            entry.setdefault("added", date.today().isoformat())
            entry["reviews"] = int(entry.get("reviews", 0))
            entry["correct_reviews"] = int(entry.get("correct_reviews", entry["reviews"]))
            entry["incorrect_reviews"] = int(entry.get("incorrect_reviews", 0))
            entry["review_streak"] = int(entry.get("review_streak", 0))
            entry.setdefault("last_reviewed", None)
            entry.setdefault("next_review", date.today().isoformat())
            self.words[word] = entry

    def save(self, path: str = "vocabulary.json"):
        Path(path).write_text(
            json.dumps(self.words, indent=2, ensure_ascii=False),
            encoding="utf-8",
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
