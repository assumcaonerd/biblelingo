"""
Parser de palavras a partir do texto dos versículos.
"""

import re
from typing import List

# Palavras muito comuns que normalmente não queremos no vocabulário inicial
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "over", "after",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "need", "dare", "ought", "used", "it", "its", "he", "she",
    "they", "them", "his", "her", "their", "this", "that", "these", "those",
    "i", "you", "we", "me", "us", "my", "your", "our"
}


def clean_word(word: str) -> str:
    """
    Remove pontuação e normaliza a palavra para minúsculas.
    Retorna string vazia se a palavra não for útil.
    """
    # Remove tudo que não for letra ou apóstrofo (para palavras como God's)
    normalized = str(word).replace("’", "'")
    cleaned = re.sub(r"[^a-zA-Z']", "", normalized)
    cleaned = cleaned.lower().strip("'")
    if cleaned.endswith("'s"):
        cleaned = cleaned[:-2]

    if len(cleaned) < 2:
        return ""
    return cleaned


def extract_words(verse_text: str, remove_stop_words: bool = True) -> List[str]:
    """
    Quebra o texto em uma lista de palavras limpas.
    Mantém a ordem de aparição e remove duplicatas.
    """
    tokens = verse_text.split()
    seen = set()
    result = []

    for token in tokens:
        word = clean_word(token)
        if not word:
            continue
        if remove_stop_words and word in STOP_WORDS:
            continue
        if word not in seen:
            seen.add(word)
            result.append(word)

    return result
