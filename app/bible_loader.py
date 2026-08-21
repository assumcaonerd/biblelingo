"""
Carrega os livros da World English Bible (WEB) a partir dos JSONs.
Fonte: https://github.com/TehShrike/world-english-bible
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def load_book(book_name: str, data_dir: str = "data") -> List[Dict[str, Any]]:
    """
    Carrega o JSON de um livro.
    Exemplos de book_name: "genesis", "john", "psalms"
    """
    path = Path(data_dir) / f"{book_name.lower()}.json"

    if not path.exists():
        # Tenta o sample se o arquivo completo não existir
        sample_path = Path(data_dir) / f"{book_name.lower()}_sample.json"
        if sample_path.exists():
            path = sample_path
        else:
            raise FileNotFoundError(
                f"Arquivo não encontrado: {path}\n"
                f"Baixe o JSON em: https://github.com/TehShrike/world-english-bible/tree/master/json"
            )

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_chapter(book_data: List[Dict[str, Any]], chapter: int) -> List[Dict[str, Any]]:
    """
    Retorna apenas os objetos de texto que pertencem ao capítulo pedido.
    """
    verses = []
    for item in book_data:
        if item.get("chapterNumber") == chapter and item.get("type") in ("paragraph text", "line text"):
            verses.append(item)
    return verses


def format_chapter(verses: List[Dict[str, Any]]) -> str:
    """
    Transforma a lista de versículos em um texto legível.
    Exemplo de saída:
    1 In the beginning, God created the heavens and the earth.
    2 The earth was formless and empty. ...
    """
    lines = []
    for v in verses:
        num = v.get("verseNumber", "?")
        text = v.get("value", "").strip()
        lines.append(f"{num} {text}")
    return "\n".join(lines)


def get_verse_text(verse_obj: Dict[str, Any]) -> str:
    """Extrai o texto limpo de um objeto de versículo."""
    return verse_obj.get("value", "").strip()
