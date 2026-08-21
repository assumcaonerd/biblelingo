"""
Parser de palavras a partir do texto dos versículos.
"""

import re


def clean_word(word: str) -> str:
    """
    Remove pontuação e normaliza a palavra para minúsculas.

    TODO:
    - Usar regex ou string methods para limpar
    - Retornar a palavra limpa ou string vazia se não for válida
    """
    pass


def extract_words(verse_text: str) -> list[str]:
    """
    Quebra o texto do versículo em uma lista de palavras limpas.

    TODO:
    - Separar por espaços
    - Aplicar clean_word em cada token
    - Remover duplicatas se quiser (ou manter ordem de aparição)
    - Filtrar palavras muito curtas (ex: a, of, the) se desejar
    """
    pass
