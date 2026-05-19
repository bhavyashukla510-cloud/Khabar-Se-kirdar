import asyncio
import logging
import uuid
from pathlib import Path

import edge_tts
from gtts import gTTS

from app.services.cache import tts_cache_path
from app.services.lang import EDGE_VOICES, GTTS_LANG, gtts_lang_code, gtts_tld

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs" / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_MIN_AUDIO_BYTES = 256


def _gtts_save(text: str, language: str, path: Path) -> None:
    """gTTS: force explicit lang; disable auto language detection (prevents English fallback)."""
    gl = gtts_lang_code(language)
    tld = gtts_tld(language)
    tts = gTTS(text=text, lang=gl, tld=tld, slow=False, lang_check=False)
    tts.save(str(path))
    logger.info("gTTS saved lang=%s tld=%s bytes=%s", gl, tld, path.stat().st_size if path.exists() else 0)


async def _edge_try_save(text: str, voice: str, out: Path) -> bool:
    try:
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(str(out))
        return out.exists() and out.stat().st_size >= _MIN_AUDIO_BYTES
    except Exception as e:
        logger.debug("edge voice %s failed: %s", voice, e)
        return False


async def synthesize_to_file(text: str, language: str) -> Path:
    """
    Prefer Edge neural voices (language-specific list).
    Fall back to gTTS with explicit ISO 639-1 + lang_check=False (no English override).
    """
    language = (language or "en").strip().lower()[:2]
    if language not in GTTS_LANG:
        language = "en"

    cached = tts_cache_path(language, text)
    if cached.exists() and cached.stat().st_size >= _MIN_AUDIO_BYTES:
        logger.info("TTS cache hit %s", cached.name)
        return cached

    out = OUTPUT_DIR / f"{uuid.uuid4().hex}.mp3"
    voices = EDGE_VOICES.get(language, EDGE_VOICES["en"])

    for voice in voices:
        try:
            if out.exists():
                out.unlink(missing_ok=True)
        except OSError:
            pass
        ok = await _edge_try_save(text, voice, out)
        if ok:
            logger.info("edge-tts ok voice=%s bytes=%s", voice, out.stat().st_size)
            try:
                cached.write_bytes(out.read_bytes())
            except Exception:
                pass
            return out

    logger.warning("edge-tts failed for all voices (%s); using gTTS", language)
    try:
        if out.exists():
            out.unlink(missing_ok=True)
    except OSError:
        pass

    try:
        await asyncio.to_thread(_gtts_save, text, language, out)
    except Exception as e:
        raise RuntimeError(
            "Speech synthesis failed: Edge TTS unavailable and gTTS error: "
            f"{e}. Check network and gTTS language support."
        ) from e

    if not out.exists() or out.stat().st_size < _MIN_AUDIO_BYTES:
        raise RuntimeError("TTS produced an empty or invalid audio file.")

    try:
        cached.write_bytes(out.read_bytes())
    except Exception:
        pass
    return out


def run_tts(text: str, language: str) -> Path:
    return asyncio.run(synthesize_to_file(text, language))
