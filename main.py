"""
Ponto de entrada do BibleLingo.
Fluxo atual:
1. Carrega progresso (XP + streak)
2. Carrega Gênesis 1
3. Extrai palavras novas com o parser
4. Adiciona ao vocabulário
5. Dá XP e salva tudo
"""

from app.progress import Progress
from app.bible_loader import load_book, get_chapter, format_chapter, get_verse_text
from app.parser import extract_words
from app.vocabulary import Vocabulary


def main():
    print("=== BibleLingo ===")
    print("Aprendendo inglês com a Bíblia\n")

    # 1. Carrega progresso e vocabulário
    progress = Progress()
    progress.load()

    vocab = Vocabulary()
    vocab.load()

    # 2. Carrega Gênesis
    print("Carregando Gênesis 1...")
    try:
        book = load_book("genesis")
        chapter_verses = get_chapter(book, 1)

        print("\n--- Gênesis 1 ---")
        print(format_chapter(chapter_verses))
        print("-----------------\n")

        # 3. Extrai palavras de cada versículo e adiciona ao vocabulário
        total_new = 0
        for verse in chapter_verses:
            text = get_verse_text(verse)
            words = extract_words(text)
            verse_num = verse.get("verseNumber", 0)

            new_count = vocab.add_words_from_verse(
                words,
                chapter=1,
                verse_number=verse_num,
                book="Genesis"
            )
            total_new += new_count

        print(f"Palavras novas adicionadas ao vocabulário: {total_new}")
        print(f"Total de palavras no vocabulário: {vocab.total_words()}")

        # Mostra algumas palavras aprendidas
        sample_words = list(vocab.words.keys())[:8]
        if sample_words:
            print(f"Exemplos: {', '.join(sample_words)}")

        # 4. Registra atividade + XP
        progress.record_activity()

        bonus = progress.get_streak_bonus()
        xp_base = 30 + (total_new * 5)  # 30 pela leitura + 5 por palavra nova
        xp_final = int(xp_base * bonus)

        print(f"\nBônus de streak: x{bonus}")
        progress.add_xp(xp_final, f"leitura de Gênesis 1 + {total_new} palavras novas")

        # 5. Salva tudo
        vocab.save()
        progress.save()

    except FileNotFoundError as e:
        print(e)
        print("\nO sample data/genesis_sample.json já está no repositório.")

    print("\n--- Estado atual ---")
    print(f"Nível: {progress.level}")
    print(f"XP: {progress.xp}")
    print(f"Streak: {progress.current_streak} dias")
    print(f"Palavras no vocabulário: {vocab.total_words()}")


if __name__ == "__main__":
    main()
