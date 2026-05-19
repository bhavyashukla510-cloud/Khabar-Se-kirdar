"""Content-addressed disk cache for expensive media/LLM-derived artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "outputs" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _digest(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x1e")
    return h.hexdigest()[:48]


def tts_cache_path(language: str, text: str) -> Path:
    return CACHE_DIR / f"tts_{_digest('tts', language, text)}.mp3"


def infographic_cache_paths(language: str, text: str) -> tuple[Path, Path]:
    base = f"ig_{_digest('infographic', language, text)}"
    return CACHE_DIR / f"{base}.png", CACHE_DIR / f"{base}.json"


def video_cache_paths(article: str, nar: str, sub: str) -> tuple[Path, Path]:
    base = f"vid_{_digest('video', nar, sub, article)}"
    return CACHE_DIR / f"{base}.mp4", CACHE_DIR / f"{base}.json"


def summarize_cache_path(language: str, text: str) -> Path:
    return CACHE_DIR / f"sum_{_digest('summarize', language, text)}.txt"


def read_json(path: Path) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
