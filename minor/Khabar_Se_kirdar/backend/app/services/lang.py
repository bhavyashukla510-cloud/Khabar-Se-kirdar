"""Supported UI / processing languages with native scripts (no Hinglish policy in prompts)."""

LANG_INFO: dict[str, dict[str, str]] = {
    "en": {"label": "English", "native": "English", "script": "Latin"},
    "hi": {"label": "Hindi", "native": "हिन्दी", "script": "Devanagari"},
    "mr": {"label": "Marathi", "native": "मराठी", "script": "Devanagari"},
    "ta": {"label": "Tamil", "native": "தமிழ்", "script": "Tamil"},
    "te": {"label": "Telugu", "native": "తెలుగు", "script": "Telugu"},
    "ur": {"label": "Urdu", "native": "اردو", "script": "Arabic (Nastaliq)"},
}

# Groq / OpenAI Whisper `language` parameter (ISO 639-1). Do not use BCP-47 here.
WHISPER_LANG: dict[str, str] = {
    "en": "en",
    "hi": "hi",
    "mr": "mr",
    "ta": "ta",
    "te": "te",
    "ur": "ur",
}

# gTTS `lang` must match Google Translate voice table (ISO 639-1).
# `lang_check=False` is required in gTTS or it may override with "detected" English.
GTTS_LANG: dict[str, str] = {
    "en": "en",
    "hi": "hi",
    "mr": "mr",
    "ta": "ta",
    "te": "te",
    "ur": "ur",
}

# Top-level domain hint for gTTS (Indian voices vs global English).
_GTTS_TLD_IN = {"hi", "mr", "ta", "te", "ur"}


def gtts_lang_code(ui_lang: str) -> str:
    k = (ui_lang or "en").strip().lower()[:2]
    return GTTS_LANG.get(k, "en")


def gtts_tld(ui_lang: str) -> str:
    k = (ui_lang or "en").strip().lower()[:2]
    return "co.in" if k in _GTTS_TLD_IN else "com"


# Edge neural voices — try in order until one succeeds (API / region differences).
EDGE_VOICES: dict[str, list[str]] = {
    "en": ["en-US-AriaNeural", "en-US-JennyNeural", "en-GB-SoniaNeural"],
    "hi": ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"],
    "mr": ["mr-IN-AarohiNeural", "mr-IN-ManoharNeural"],
    "ta": ["ta-IN-PallaviNeural", "ta-IN-ValluvarNeural"],
    "te": ["te-IN-ShrutiNeural", "te-IN-MohanNeural"],
    "ur": ["ur-PK-AsadNeural", "ur-IN-SalmanNeural"],
}

# Backwards compatibility
EDGE_VOICE: dict[str, str] = {k: v[0] for k, v in EDGE_VOICES.items()}


def list_languages() -> list[dict[str, str]]:
    return [{"code": code, **meta} for code, meta in LANG_INFO.items()]
