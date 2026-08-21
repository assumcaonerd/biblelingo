"""
Ponto de entrada do BibleLingo.
Suporte a múltiplos idiomas nativos (pt, es, en, ar, he) com RTL.
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
    is_rtl,
)
from app.rtl import prepare_rtl, is_rtl_available


def t(text: str, lang: str) -> str:
    """Aplica formatação RTL quando necessário."""
    if is_rtl(lang):
        return prepare_rtl(text, lang)
    return text


def choose_language() -> str:
    """Pergunta ao usuário qual é o idioma nativo dele."""
    print("Idiomas disponíveis / Available languages:")
    for code, info in SUPPORTED_NATIVE_LANGUAGES.items():
        name = info["name"]
        if info.get("rtl"):
            name = prepare_rtl(name, code)
        print(f"  {code} – {info['flag']} {name}")

    codes = ", ".join(SUPPORTED_NATIVE_LANGUAGES.keys())
    while True:
        choice = input(f"\nSeu idioma nativo [{DEFAULT_NATIVE}]: ").strip().lower()
        if not choice:
            return DEFAULT_NATIVE
        if choice in SUPPORTED_NATIVE_LANGUAGES:
            return choice
        print(f"Opção inválida. Use: {codes}")


def main():
    native_lang = choose_language()
    ui = get_ui(native_lang)

    if is_rtl(native_lang) and not is_rtl_available():
        print("Aviso: para melhor exibição de árabe/hebraico, instale:")
        print("  pip install arabic-reshaper python-bidi\n")

    print(f"\n=== {ui['app_title']} ===")
    print(t(ui["subtitle"], native_lang))
    native_name = get_native_language_name(native_lang)
    print(
        f"{t('Idioma nativo', native_lang)}: "
        f"{prepare_rtl(native_name, native_lang) if is_rtl(native_lang) else native_name}\n"
    )

    progress = Progress()
    progress.load()

    vocab = Vocabulary()
    vocab.load()

    dictionary = load_dictionary()

    print(t(ui["loading_chapter"], native_lang))
    try:
        book = load_book("genesis")
        chapter_verses = get_chapter(book, 1)
        chapter_text = format_chapter(chapter_verses)

        print("\n--- Genesis 1 ---")
        print(chapter_text)
        print("-----------------\n")

        try:
            from app.audio import speak
            hear = input(t(ui["hear_text"], native_lang)).strip().lower()
            if hear in ("s", "sim", "y", "yes", "ن", "כ"):
                first_verses = " ".join(
                    get_verse_text(v) for v in chapter_verses[:4]
                )
                print(f"{t(ui['playing'], native_lang)}\n")
                speak(first_verses)
        except Exception as exc:
            print(f"({t(ui['audio_unavailable'], native_lang)}: {exc})")
            print(f"{ui['install_audio']}\n")

        total_new = 0
        for verse in chapter_verses:
            text = get_verse_text(verse)
            words = extract_words(text)
            verse_num = verse.get("verseNumber", 0)

            new_count = vocab.add_words_from_verse(
                words,
                chapter=1,
                verse_number=verse_num,
                book="Genesis",
                verse_text=text,
            )
            total_new += new_count

        print(f"\n{t(ui['new_words'], native_lang)}: {total_new}")
        print(f"{t(ui['total_words'], native_lang)}: {vocab.total_words()}")

        sample_words = list(vocab.words.keys())[:8]
        if sample_words:
            print(f"{t(ui['examples'], native_lang)}: {', '.join(sample_words)}")

        quiz_words = vocab.get_words_for_quiz(limit=5)
        contexts = {
            word: vocab.words.get(word, {}).get("context", "")
            for word in quiz_words
        }
        questions = generate_quiz(
            quiz_words,
            dictionary,
            native_lang=native_lang,
            limit=5,
            contexts=contexts,
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
            print(f"\n{t(ui['quiz_unavailable'], native_lang)}")
            quiz_xp = 0
            result = {"correct": 0, "incorrect": 0, "total": 0}

        progress.record_activity()

        bonus = progress.get_streak_bonus()
        xp_base = 30 + (total_new * 5) + quiz_xp
        xp_final = int(xp_base * bonus)

        print(f"\n{t(ui['streak_bonus'], native_lang)}: x{bonus}")
        progress.add_xp(
            xp_final,
            f"leitura + {total_new} palavras + {result['correct']} acertos",
        )

        vocab.save()
        progress.save()

    except FileNotFoundError as exc:
        print(exc)
        print("\nO sample data/genesis_sample.json já está no repositório.")

    print("\n--- Estado atual ---")
    print(f"{t(ui['level'], native_lang)}: {progress.level}")
    print(f"{ui['xp']}: {progress.xp}")
    print(f"{t(ui['streak'], native_lang)}: {progress.current_streak} {t(ui['days'], native_lang)}")
    print(f"{t(ui['words_in_vocab'], native_lang)}: {vocab.total_words()}")
    level_progress = progress.level_progress()
    print(
        f"{t(ui['level_progress'], native_lang)}: "
        f"{level_progress['current']}/{level_progress['next_level']} XP "
        f"({level_progress['percent']}%)"
    )


if __name__ == "__main__":
    main()
