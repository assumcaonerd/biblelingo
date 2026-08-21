"""
Ponto de entrada do BibleLingo.
Por enquanto só testa o sistema de XP e Streak.
"""

from app.progress import Progress


def main():
    print("=== BibleLingo ===")
    print("Aprendendo inglês com a Bíblia\n")

    progress = Progress()
    progress.load()

    print("\nRegistrando atividade de hoje...")
    progress.record_activity()

    # Simula ganhar XP por ler um capítulo
    bonus = progress.get_streak_bonus()
    xp_base = 30
    xp_final = int(xp_base * bonus)

    print(f"\nBônus de streak atual: x{bonus}")
    progress.add_xp(xp_final, "leitura de capítulo (simulado)")

    progress.save()

    print("\n--- Estado atual ---")
    print(f"Nível: {progress.level}")
    print(f"XP: {progress.xp}")
    print(f"Streak: {progress.current_streak} dias")
    print(f"Recorde de streak: {progress.longest_streak} dias")


if __name__ == "__main__":
    main()
