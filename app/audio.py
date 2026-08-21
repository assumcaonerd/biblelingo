"""
Módulo de áudio do BibleLingo.
Usa edge-tts (Microsoft Edge TTS) – gratuito, alta qualidade e sem necessidade de API key.

Instalação:
    pip install edge-tts

Uso básico:
    from app.audio import speak, save_audio
    speak("In the beginning, God created the heavens and the earth.")
"""

import asyncio
import edge_tts
from pathlib import Path
from typing import Optional

# Voz padrão (inglês americano natural)
DEFAULT_VOICE = "en-US-AriaNeural"   # feminina, clara
# Outras boas opções:
# "en-US-GuyNeural"      → masculina
# "en-US-JennyNeural"    → feminina
# "en-GB-SoniaNeural"    → britânica


async def _generate_audio(text: str, voice: str = DEFAULT_VOICE) -> bytes:
    """Gera o áudio em memória."""
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data


def speak(text: str, voice: str = DEFAULT_VOICE):
    """
    Fala o texto usando o alto-falante do computador.
    Funciona de forma síncrona (bloqueia até terminar).
    """
    try:
        import tempfile
        import subprocess
        import sys

        audio_bytes = asyncio.run(_generate_audio(text, voice))

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        # Toca o arquivo de forma simples e multiplataforma
        if sys.platform == "darwin":
            subprocess.run(["afplay", temp_path], check=False)
        elif sys.platform.startswith("linux"):
            # tenta mpg123, depois ffplay, depois aplay
            for player in (["mpg123", "-q"], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"], ["aplay"]):
                try:
                    subprocess.run(player + [temp_path], check=True)
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
        elif sys.platform == "win32":
            subprocess.run(["start", temp_path], shell=True, check=False)

        Path(temp_path).unlink(missing_ok=True)

    except Exception as e:
        print(f"[Áudio] Não foi possível reproduzir: {e}")
        print(f"Texto que seria falado: {text}")


def save_audio(text: str, filename: str, voice: str = DEFAULT_VOICE):
    """
    Salva o áudio em um arquivo .mp3.
    Útil para cachear pronúncias de palavras frequentes.
    """
    audio_bytes = asyncio.run(_generate_audio(text, voice))
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(audio_bytes)
    print(f"Áudio salvo em: {path}")
    return str(path)


def speak_word(word: str, voice: str = DEFAULT_VOICE):
    """Atalho para falar uma única palavra (mais lento e claro)."""
    # Adiciona uma pequena pausa mental falando a palavra isolada
    speak(word, voice)


def list_voices():
    """Lista algumas vozes em inglês disponíveis."""
    print("Vozes recomendadas:")
    print("  en-US-AriaNeural   → americana feminina (padrão)")
    print("  en-US-GuyNeural    → americana masculina")
    print("  en-US-JennyNeural  → americana feminina")
    print("  en-GB-SoniaNeural  → britânica")
