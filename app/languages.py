"""
Configuração de idiomas do BibleLingo.

Idioma de aprendizado (target): inglês (WEB)
Idioma nativo do usuário (source): português, espanhol, etc.
"""

from typing import Dict

# Idiomas suportados como língua nativa do usuário
SUPPORTED_NATIVE_LANGUAGES = {
    "pt": {
        "code": "pt",
        "name": "Português",
        "name_en": "Portuguese",
        "flag": "🇧🇷",
    },
    "es": {
        "code": "es",
        "name": "Español",
        "name_en": "Spanish",
        "flag": "🇪🇸",
    },
    "en": {
        "code": "en",
        "name": "English",
        "name_en": "English",
        "flag": "🇺🇸",
    },
}

# Idioma padrão do usuário (brasileiro)
DEFAULT_NATIVE = "pt"

# Idioma que estamos aprendendo (sempre inglês por enquanto)
TARGET_LANGUAGE = "en"
TARGET_LANGUAGE_NAME = "English"

# Textos da interface em cada idioma nativo
UI_STRINGS: Dict[str, Dict[str, str]] = {
    "pt": {
        "app_title": "BibleLingo",
        "subtitle": "Aprendendo inglês com a Bíblia",
        "loading_chapter": "Carregando Gênesis 1...",
        "hear_text": "Quer ouvir o texto em inglês? (s/n): ",
        "playing": "Reproduzindo...",
        "new_words": "Palavras novas adicionadas",
        "total_words": "Total no vocabulário",
        "examples": "Exemplos",
        "quiz_title": "Quiz",
        "hear_pronunciation": "Ouvir pronúncia? (s/n): ",
        "your_answer": "Sua resposta (número): ",
        "correct": "Correto!",
        "wrong": "Errado. A resposta certa é",
        "result": "Resultado",
        "hits": "acertos",
        "streak_bonus": "Bônus de streak",
        "level": "Nível",
        "xp": "XP",
        "streak": "Streak",
        "days": "dias",
        "words_in_vocab": "Palavras no vocabulário",
        "choose_language": "Escolha seu idioma nativo",
        "meaning_of": "Qual o significado de",
        "audio_unavailable": "Áudio indisponível",
        "install_audio": "Instale com: pip install edge-tts",
    },
    "es": {
        "app_title": "BibleLingo",
        "subtitle": "Aprendiendo inglés con la Biblia",
        "loading_chapter": "Cargando Génesis 1...",
        "hear_text": "¿Quieres escuchar el texto en inglés? (s/n): ",
        "playing": "Reproduciendo...",
        "new_words": "Palabras nuevas añadidas",
        "total_words": "Total en el vocabulario",
        "examples": "Ejemplos",
        "quiz_title": "Quiz",
        "hear_pronunciation": "¿Escuchar pronunciación? (s/n): ",
        "your_answer": "Tu respuesta (número): ",
        "correct": "¡Correcto!",
        "wrong": "Incorrecto. La respuesta correcta es",
        "result": "Resultado",
        "hits": "aciertos",
        "streak_bonus": "Bonus de racha",
        "level": "Nivel",
        "xp": "XP",
        "streak": "Racha",
        "days": "días",
        "words_in_vocab": "Palabras en el vocabulario",
        "choose_language": "Elige tu idioma nativo",
        "meaning_of": "¿Cuál es el significado de",
        "audio_unavailable": "Audio no disponible",
        "install_audio": "Instala con: pip install edge-tts",
    },
    "en": {
        "app_title": "BibleLingo",
        "subtitle": "Learning English with the Bible",
        "loading_chapter": "Loading Genesis 1...",
        "hear_text": "Do you want to hear the text in English? (y/n): ",
        "playing": "Playing...",
        "new_words": "New words added",
        "total_words": "Total in vocabulary",
        "examples": "Examples",
        "quiz_title": "Quiz",
        "hear_pronunciation": "Hear pronunciation? (y/n): ",
        "your_answer": "Your answer (number): ",
        "correct": "Correct!",
        "wrong": "Wrong. The correct answer is",
        "result": "Result",
        "hits": "correct",
        "streak_bonus": "Streak bonus",
        "level": "Level",
        "xp": "XP",
        "streak": "Streak",
        "days": "days",
        "words_in_vocab": "Words in vocabulary",
        "choose_language": "Choose your native language",
        "meaning_of": "What is the meaning of",
        "audio_unavailable": "Audio unavailable",
        "install_audio": "Install with: pip install edge-tts",
    },
}


def get_ui(lang: str = DEFAULT_NATIVE) -> Dict[str, str]:
    """Retorna os textos da interface no idioma pedido."""
    return UI_STRINGS.get(lang, UI_STRINGS[DEFAULT_NATIVE])


def get_native_language_name(code: str) -> str:
    lang = SUPPORTED_NATIVE_LANGUAGES.get(code)
    return lang["name"] if lang else code
