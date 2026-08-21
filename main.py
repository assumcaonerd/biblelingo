"""
Ponto de entrada do BibleLingo.
Testa o carregamento de Gênesis + sistema de XP e Streak.
"""

from app.progress import Progress
from app.bible_loader import load_book, get_chapter, format_chapter


def main():
    print("=== BibleLingo ===")
    print("Aprendendo inglês com a Bíblia\n")

    # 1. Carrega o progresso
    progress = Progress()
    progress.load()

    # 2. Carrega Gênesis (usa o sample se o arquivo completo não existir)
    print("Carregando Gênesis...")
    try:
        book = load_book("genesis")
        chapter = get_chapter(book, 1)
        text = format_chapter(chapter)

        print("\n--- Gênesis 1 ---")
        print(text)
        print("-----------------\n")

        # Registra a atividade e dá XP pela leitura
        progress.record_activity()

        bonus = progress.get_streak_bonus()
        xp_base = 30
        xp_final = int(xp_base * bonus)

        print(f"Bônus de streak: x{bonus}")
        progress.add_xp(xp_final, "leitura de Gênesis 1")

    except FileNotFoundError as e:
        print(e)
        print("\nColoque o arquivo data/genesis.json ou use o sample que já está no repositório.")

    progress.save()

    print("\n--- Estado atual ---")
    print(f"Nível: {progress.level}")
    print(f"XP: {progress.xp}")
    print(f"Streak: {progress.current_streak} dias")
    print(f"Recorde de streak: {progress.longest_streak} dias")


if __name__ == "__main__":
    main()
