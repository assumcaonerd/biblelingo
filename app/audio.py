"""
Módulo de áudio do BibleLingo.
Usa edge-tts (Microsoft Edge TTS) – gratuito, alta qualidade e sem API key.

Novidades:
- Cache automático das pronúncias (pasta data/audio_cache/)
- Controle de velocidade (rate)
- Funções para falar palavra ou texto completo

Instalação:
    pip install edge-tts
"""

import asyncio
import hashlib
import shutil
from pathlib import Path

try:
    import edge_tts
except ImportError:  # áudio é opcional; o restante do app continua funcional
    edge_tts = None
from typing import Optional
import subprocess
import sys
import tempfile

# Voz padrão (inglês americano natural)
DEFAULT_VOICE = "en-US-AriaNeural"

# Velocidade padrão ("-20%" = mais lento e claro para aprendizado)
DEFAULT_RATE = "-15%"

# Onde guardar os áudios em cache
CACHE_DIR = Path("data/audio_cache")


def _cache_key(text: str, voice: str, rate: str) -> str:
    """Gera um nome de arquivo único para o texto + voz + velocidade."""
    raw = f"{text}|{voice}|{rate}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


async def _generate_audio(text: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE) -> bytes:
    """Gera o áudio em memória usando edge-tts."""
    if edge_tts is None:
        raise RuntimeError("edge-tts não está instalado; execute pip install -r requirements.txt")
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data


def _get_or_create_audio(text: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE) -> Path:
    """
    Retorna o caminho do arquivo de áudio.
    Se já existir no cache, reutiliza. Caso contrário, gera e salva.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    key = _cache_key(text, voice, rate)
    cache_path = CACHE_DIR / f"{key}.mp3"

    if cache_path.exists() and cache_path.stat().st_size > 0:
        return cache_path

    # Gera e salva no cache
    audio_bytes = asyncio.run(_generate_audio(text, voice, rate))
    cache_path.write_bytes(audio_bytes)
    return cache_path


def _play_file(path: Path):
    """Toca um arquivo de áudio de forma multiplataforma."""
    path_str = str(path)

    if sys.platform == "darwin":
        subprocess.run(["afplay", path_str], check=False)
    elif sys.platform.startswith("linux"):
        for player in (
            ["mpg123", "-q"],
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
            ["aplay"],
        ):
            if shutil.which(player[0]) is None:
                continue
            try:
                subprocess.run(player + [path_str], check=True)
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        print("[Áudio] Nenhum player encontrado (mpg123, ffplay ou aplay).")
    elif sys.platform == "win32":
        subprocess.run(["start", "", path_str], shell=True, check=False)


def speak(text: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE):
    """
    Fala o texto.
    Usa cache automaticamente.
    """
    try:
        path = _get_or_create_audio(text, voice, rate)
        _play_file(path)
    except Exception as e:
        print(f"[Áudio] Erro: {e}")
        print(f"Texto: {text}")


def speak_word(word: str, voice: str = DEFAULT_VOICE, rate: str = "-25%"):
    """
    Fala uma palavra isolada (mais lento por padrão para ficar bem claro).
    """
    speak(word, voice=voice, rate=rate)


def save_audio(text: str, filename: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE) -> str:
    """
    Salva o áudio em um arquivo específico (além do cache).
    """
    path = _get_or_create_audio(text, voice, rate)
    target = Path(filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(path.read_bytes())
    print(f"Áudio salvo em: {target}")
    return str(target)


def clear_cache():
    """Apaga todos os arquivos de cache de áudio."""
    if CACHE_DIR.exists():
        count = 0
        for f in CACHE_DIR.glob("*.mp3"):
            f.unlink()
            count += 1
        print(f"Cache limpo: {count} arquivos removidos.")
    else:
        print("Nenhum cache encontrado.")


def list_voices():
    """Mostra as vozes recomendadas."""
    print("Vozes recomendadas:")
    print("  en-US-AriaNeural   → americana feminina (padrão)")
    print("  en-US-GuyNeural    → americana masculina")
    print("  en-US-JennyNeural  → americana feminina")
    print("  en-GB-SoniaNeural  → britânica")
    print("\nVelocidade (rate):")
    print('  "-25%"  → bem lento (bom para palavras isoladas)')
    print('  "-15%"  → um pouco mais lento (padrão)')
    print('  "+0%"   → velocidade normal')
    print('  "+20%"  → mais rápido')
