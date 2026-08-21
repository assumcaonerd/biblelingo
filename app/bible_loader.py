"""
Carrega os livros da World English Bible (WEB) a partir dos JSONs.
Fonte recomendada: https://github.com/TehShrike/world-english-bible
"""

import json
from pathlib import Path


def load_book(book_name: str, data_dir: str = "data") -> list:
    """
    Carrega o JSON de um livro.
    Exemplo: load_book("genesis")

    TODO:
    - Verificar se o arquivo existe
    - Carregar o JSON
    - Retornar a lista de objetos do livro
    """
    pass


def get_chapter(book_data: list, chapter: int) -> list:
    """
    Filtra apenas os versículos de um capítulo específico.

    TODO:
    - Percorrer book_data
    - Manter apenas itens que tenham chapterNumber == chapter
      e que sejam do tipo texto (paragraph text ou line text)
    - Retornar lista limpa de versículos
    """
    pass


def get_verse_text(verse_obj: dict) -> str:
    """
    Extrai o texto limpo de um objeto de versículo.
    """
    return verse_obj.get("value", "").strip()
