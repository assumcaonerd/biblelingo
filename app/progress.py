"""
Sistema de progresso do BibleLingo.
Cuida de XP, níveis e streak de dias consecutivos.
"""

from datetime import date, timedelta
import json
from pathlib import Path


class Progress:
    def __init__(self):
        self.xp = 0
        self.level = 1
        self.current_streak = 0
        self.longest_streak = 0
        self.last_activity_date = None  # date ou None
        self.vocabulary = {}           # será usado depois

    # ------------------------------------------------------------------
    # XP e Níveis
    # ------------------------------------------------------------------
    def xp_for_level(self, level: int) -> int:
        """Quantidade de XP necessária para alcançar um determinado nível.
        Fórmula simples e progressiva.
        """
        if level <= 1:
            return 0
        # Nível 2 = 100, 3 = 250, 4 = 500, 5 = 850...
        return int(50 * (level ** 1.8))

    def add_xp(self, amount: int, reason: str = "") -> bool:
        """
        Adiciona XP e verifica se o usuário subiu de nível.
        Retorna True se subiu de nível.
        """
        if amount <= 0:
            return False

        old_level = self.level
        self.xp += amount

        # Verifica quantos níveis subiu (pode subir mais de um de uma vez)
        while self.xp >= self.xp_for_level(self.level + 1):
            self.level += 1

        leveled_up = self.level > old_level

        if reason:
            print(f"+{amount} XP ({reason}) | Total: {self.xp} XP | Nível {self.level}")
        else:
            print(f"+{amount} XP | Total: {self.xp} XP | Nível {self.level}")

        if leveled_up:
            print(f"*** Subiu para o nível {self.level}! ***")

        return leveled_up

    # ------------------------------------------------------------------
    # Streak
    # ------------------------------------------------------------------
    def record_activity(self):
        """
        Registra que o usuário fez alguma atividade válida hoje.
        Atualiza o streak corretamente.
        """
        today = date.today()

        if self.last_activity_date is None:
            # Primeira atividade de sempre
            self.current_streak = 1
            self.last_activity_date = today
        elif self.last_activity_date == today:
            # Já registrou atividade hoje → não faz nada
            return
        elif self.last_activity_date == today - timedelta(days=1):
            # Continuou a sequência
            self.current_streak += 1
        else:
            # Quebrou a sequência
            self.current_streak = 1

        self.last_activity_date = today

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        print(f"Streak atual: {self.current_streak} dia(s) | Recorde: {self.longest_streak}")

    def get_streak_bonus(self) -> float:
        """
        Multiplicador de XP baseado no streak atual.
        """
        if self.current_streak >= 30:
            return 1.5
        if self.current_streak >= 7:
            return 1.2
        return 1.0

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "xp": self.xp,
            "level": self.level,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_activity_date": self.last_activity_date.isoformat() if self.last_activity_date else None,
            "vocabulary": self.vocabulary,
        }

    def from_dict(self, data: dict):
        self.xp = data.get("xp", 0)
        self.level = data.get("level", 1)
        self.current_streak = data.get("current_streak", 0)
        self.longest_streak = data.get("longest_streak", 0)

        last = data.get("last_activity_date")
        self.last_activity_date = date.fromisoformat(last) if last else None

        self.vocabulary = data.get("vocabulary", {})

    def save(self, path: str = "progress.json"):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))
        print(f"Progresso salvo em {path}")

    def load(self, path: str = "progress.json"):
        file = Path(path)
        if not file.exists():
            print("Nenhum progresso anterior encontrado. Começando do zero.")
            return

        data = json.loads(file.read_text())
        self.from_dict(data)
        print(f"Progresso carregado: Nível {self.level} | {self.xp} XP | Streak {self.current_streak}")


# ------------------------------------------------------------------
# Função auxiliar para testes rápidos
# ------------------------------------------------------------------
if __name__ == "__main__":
    p = Progress()
    p.load()

    print("\n--- Simulando atividade ---")
    p.record_activity()

    bonus = p.get_streak_bonus()
    xp_base = 30
    xp_final = int(xp_base * bonus)

    p.add_xp(xp_final, "leitura de capítulo")
    p.save()
