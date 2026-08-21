"""
Ponto de entrada do BibleLingo.
Fluxo atual:
1. Carrega progresso (XP + streak)
2. Carrega Gênesis 1
3. Oferece ouvir o texto
4. Extrai palavras e adiciona ao vocabulário
5. Roda um quiz (com opção de ouvir a pronúncia)
6. Dá XP e salva tudo
"""

from app.progress import Progress
from app.bible_loader import load_book, get_chapter, format_chapter, get_verse_text
from app.parser import extract_words
from app.vocabulary import Vocabulary
from app.quiz import load_dictionary, generate_quiz, run_quiz


def main():
    print("=== BibleLingo ===")
    print("Aprendendo inglês com a Bíblia\n")

    # 1. Carrega progresso e vocabulário
    progress = Progress()
    progress.load()

    vocab = Vocabulary()
    vocab.load()

    dictionary = load_dictionary()

    # 2. Carrega Gênesis
    print("Carregando Gênesis 1...")
    try:
        book = load_book("genesis")
        chapter_verses = get_chapter(book, 1)
        chapter_text = format_chapter(chapter_verses)

        print("\n--- Gênesis 1 ---")
        print(chapter_text)
        print("-----------------\n")

        # Oferece ouvir o capítulo (ou os primeiros versículos)
        try:
            from app.audio import speak
            hear = input("Quer ouvir o texto em inglês? (s/n): ").strip().lower()
            if hear in ("s", "sim", "y", "yes"):
                # Fala só os primeiros versículos para não ficar muito longo
                first_verses = " ".join(
                    get_verse_text(v) for v in chapter_verses[:4]
                )
                print("Reproduzindo...\n")
                speak(first_verses)
        except Exception as e:
            print(f"(Áudio indisponível: {e})")
            print("Instale com: pip install edge-tts\n")

        # 3. Extrai palavras e adiciona ao vocabulário
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

        print(f"\nPalavras novas adicionadas: {total_new}")
        print(f"Total no vocabulário: {vocab.total_words()}")

        sample_words = list(vocab.words.keys())[:8]
        if sample_words:
            print(f"Exemplos: {', '.join(sample_words)}")

        # 4. Gera e roda o quiz
        quiz_words = vocab.get_words_for_quiz(limit=5)
        questions = generate_quiz(quiz_words, dictionary, limit=5)

        if questions:
            result = run_quiz(questions, vocabulary=vocab, enable_audio=True)
            quiz_xp = result["correct"] * 10
        else:
            print("\nAinda não há palavras suficientes no dicionário para o quiz.")
            quiz_xp = 0
            result = {"correct": 0, "total": 0}

        # 5. Registra atividade + XP total
        progress.record_activity()

        bonus = progress.get_streak_bonus()
        xp_base = 30 + (total_new * 5) + quiz_xp
        xp_final = int(xp_base * bonus)

        print(f"\nBônus de streak: x{bonus}")
        progress.add_xp(
            xp_final,
            f"leitura + {total_new} palavras + {result['correct']} acertos no quiz"
        )

        # 6. Salva tudo
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
