import logging
import os
import uuid
from pathlib import Path

import httpx
from pydub import AudioSegment

from app.config import get_settings
from app.services.lang import WHISPER_LANG

logger = logging.getLogger(__name__)

OUTPUT_TMP = Path(__file__).resolve().parent.parent.parent / "outputs" / "tmp"
OUTPUT_TMP.mkdir(parents=True, exist_ok=True)

_WHISPER_PROMPT: dict[str, str] = {
    "en": "This is English news or interview audio.",
    "hi": "यह हिंदी में बोला गया समाचार या साक्षात्कार है।",
    "mr": "हे मराठीत बोललेले बातमी किंवा मुलाखत आहे.",
    "ta": "இது தமிழில் பேசப்பட்ட செய்தி அல்லது நேர்காணல்.",
    "te": "ఇది తెలుగులో మాట్లాడిన వార్త లేదా ఇంటర్వ్యూ.",
    "ur": "یہ اردو میں بولی گئی خبر یا انٹرویو ہے۔",
}

_STT_MODELS = ("whisper-large-v3-turbo", "whisper-large-v3")


def _normalize_audio(input_path: Path) -> Path:
    ext = input_path.suffix.lower()
    out = OUTPUT_TMP / f"{uuid.uuid4().hex}_16k.wav"
    try:
        seg = AudioSegment.from_file(str(input_path), format=ext.lstrip(".") or None)
        seg = seg.set_channels(1).set_frame_rate(16000)
        seg.export(str(out), format="wav")
        return out
    except Exception as e:
        logger.warning("audio normalize failed, using original: %s", e)
        return input_path


def transcribe_file(path: Path, language: str | None = None) -> str:
    settings = get_settings()
    key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is required for speech-to-text.")

    lang = (language or "en").strip().lower()[:2]
    if lang not in WHISPER_LANG:
        raise RuntimeError(f"Unsupported STT language code: {language!r}. Use en, hi, mr, ta, te, or ur.")

    whisper_lang = WHISPER_LANG[lang]
    prompt = _WHISPER_PROMPT.get(lang, _WHISPER_PROMPT["en"])[:224]

    wav = _normalize_audio(path)
    try:
        with open(wav, "rb") as f:
            file_bytes = f.read()

        filename = Path(wav).name
        mime = "audio/wav"

        last_err: str | None = None
        with httpx.Client(timeout=180.0) as client:
            for model in _STT_MODELS:
                data = {
                    "model": model,
                    "temperature": "0",
                    "language": whisper_lang,
                    "prompt": prompt,
                }
                logger.info("STT model=%s language=%s whisper=%s", model, lang, whisper_lang)
                r = client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {key}"},
                    files={"file": (filename, file_bytes, mime)},
                    data=data,
                )
                if r.status_code >= 400:
                    last_err = r.text or f"HTTP {r.status_code}"
                    logger.warning("STT model %s failed: %s", model, last_err[:200])
                    continue
                js = r.json()
                text = (js.get("text") or "").strip()
                if not text:
                    logger.warning("STT empty transcript for language=%s model=%s", lang, model)
                return text

        raise RuntimeError(last_err or "STT failed for all models")
    finally:
        if wav != path and wav.exists():
            try:
                wav.unlink()
            except OSError:
                pass
