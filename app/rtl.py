"""
Suporte a texto RTL (Right-to-Left) para árabe e hebraico.

Usa:
- arabic-reshaper  → conecta as letras árabes corretamente
- python-bidi      → aplica o algoritmo bidirecional do Unicode

Instalação:
    pip install arabic-reshaper python-bidi

Se as bibliotecas não estiverem instaladas, o texto é retornado sem alteração
(ainda legível em terminais modernos com suporte a Unicode).
"""

from typing import Optional

# Tenta importar as bibliotecas de RTL
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    RTL_AVAILABLE = True
except ImportError:
    RTL_AVAILABLE = False


def prepare_rtl(text: str, lang: Optional[str] = None) -> str:
    """
    Prepara texto RTL para exibição correta no terminal.

    - Para árabe: faz o reshape das letras + algoritmo bidi
    - Para hebraico: aplica principalmente o algoritmo bidi
    - Para outros idiomas: devolve o texto original

    Args:
        text: texto original (lógico)
        lang: código do idioma ('ar', 'he', etc.). Opcional.

    Returns:
        Texto pronto para ser impresso no terminal.
    """
    if not text or not text.strip():
        return text

    if not RTL_AVAILABLE:
        return text

    # Árabe precisa de reshape (as letras mudam de forma conforme a posição)
    if lang == "ar" or _contains_arabic(text):
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text

    # Hebraico e outros RTL: só o algoritmo bidi
    if lang == "he" or _contains_hebrew(text):
        try:
            return get_display(text)
        except Exception:
            return text

    return text


def print_rtl(text: str, lang: Optional[str] = None, end: str = "\n"):
    """
    Imprime texto com suporte a RTL.
    Atalho conveniente para print(prepare_rtl(...)).
    """
    print(prepare_rtl(text, lang), end=end)


def _contains_arabic(text: str) -> bool:
    """Verifica se o texto contém caracteres árabes."""
    for ch in text:
        if "\u0600" <= ch <= "\u06FF" or "\u0750" <= ch <= "\u077F":
            return True
    return False


def _contains_hebrew(text: str) -> bool:
    """Verifica se o texto contém caracteres hebraicos."""
    for ch in text:
        if "\u0590" <= ch <= "\u05FF":
            return True
    return False


def is_rtl_available() -> bool:
    """Retorna True se as bibliotecas de RTL estão instaladas."""
    return RTL_AVAILABLE
