"""
Ponto de entrada do BibleLingo.
Suporte a múltiplos idiomas nativos (pt, es, en).
"""

from app.progress import Progress
from app.bible_loader import load_book, get_chapter, format_chapter, get_verse_text
from app.parser import extract_words
from app.vocabulary import Vocabulary
from app.quiz import load_dictionary, generate_quiz, run_quiz
from app.languages import (
    DEFAULT_NATIVE,
    SUPPORTED_NATIVE_LANGUAGES,
    get_ui,
    get_native_language_name,
)


def choose_language() -> str:
    """Pergunta ao usuário qual é o idioma nativo dele."""
    print("Idiomas disponíveis:")
    for code, info in SUPPORTED_NATIVE_LANGUAGES.items():
        print(f"  {code} – {info['flag']} {info['name']}")

    while True:
        choice = input(f"\nSeu idioma nativo [{DEFAULT_NATIVE}]: ").strip().lower()
        if not choice:
            return DEFAULT_NATIVE
        if choice in SUPPORTED_NATIVE_LANGUAGES:
            return choice
        print("Opção inválida. Use: pt, es ou en")


def main():
    # Escolha do idioma nativo
    native_lang = choose_language()
    ui = get_ui(native_lang)

    print(f"\n=== {ui['app_title']} ===")
    print(f"{ui['subtitle']}")
    print(f"Idioma nativo: {get_native_language_name(native_lang)}\n")

    # 1. Carrega progresso e vocabulário
    progress = Progress()
    progress.load()

    vocab = Vocabulary()
    vocab.load()

    dictionary = load_dictionary()

    # 2. Carrega Gênesis
    print(ui["loading_chapter"])
    try:
        book = load_book("genesis")
        chapter_verses = get_chapter(book, 1)
        chapter_text = format_chapter(chapter_verses)

        print("\n--- Genesis 1 ---")
        print(chapter_text)
        print("-----------------\n")

        # Oferece ouvir o capítulo
        try:
            from app.audio import speak
            hear = input(ui["hear_text"]).strip().lower()
            if hear in ("s", "sim", "y", "yes"):
                first_verses = " ".join(
                    get_verse_text(v) for v in chapter_verses[:4]
                )
                print(f"{ui['playing']}\n")
                speak(first_verses)
        except Exception as e:
            print(f"({ui['audio_unavailable']}: {e})")
            print(f"{ui['install_audio']}\n")

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

        print(f"\n{ui['new_words']}: {total_new}")
        print(f"{ui['total_words']}: {vocab.total_words()}")

        sample_words = list(vocab.words.keys())[:8]
        if sample_words:
            print(f"{ui['examples']}: {', '.join(sample_words)}")

        # 4. Gera e roda o quiz no idioma nativo escolhido
        quiz_words = vocab.get_words_for_quiz(limit=5)
        questions = generate_quiz(
            quiz_words,
            dictionary,
            native_lang=native_lang,
            limit=5
        )

        if questions:
            result = run_quiz(
                questions,
                vocabulary=vocab,
                enable_audio=True,
                native_lang=native_lang,
            )
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

        print(f"\n{ui['streak_bonus']}: x{bonus}")
        progress.add_xp(
            xp_final,
            f"leitura + {total_new} palavras + {result['correct']} acertos"
        )

        # 6. Salva tudo
        vocab.save()
        progress.save()

    except FileNotFoundError as e:
        print(e)
        print("\nO sample data/genesis_sample.json já está no repositório.")

    print(f"\n--- Estado atual ---")
    print(f"{ui['level']}: {progress.level}")
    print(f"{ui['xp']}: {progress.xp}")
    print(f"{ui['streak']}: {progress.current_streak} {ui['days']}")
    print(f"{ui['words_in_vocab']}: {vocab.total_words()}")


if __name__ == "__main__":
    main()
