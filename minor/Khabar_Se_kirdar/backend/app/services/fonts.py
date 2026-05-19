"""Resolve and optionally download Noto fonts for Pillow / Matplotlib Unicode rendering."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
FONT_DIR.mkdir(parents=True, exist_ok=True)

_download_lock = threading.Lock()

# googlefonts/noto-fonts main — Regular TTFs (hinted)
_NOTO_BASE = "https://raw.githubusercontent.com/googlefonts/noto-fonts/main/hinted/ttf"

_FONT_FILES: dict[str, tuple[str, str]] = {
    "devanagari": ("NotoSansDevanagari", "NotoSansDevanagari-Regular.ttf"),
    "tamil": ("NotoSansTamil", "NotoSansTamil-Regular.ttf"),
    "telugu": ("NotoSansTelugu", "NotoSansTelugu-Regular.ttf"),
    "urdu": ("NotoNastaliqUrdu", "NotoNastaliqUrdu-Regular.ttf"),
    "latin": ("NotoSans", "NotoSans-Regular.ttf"),
}

# Language code → primary script bundle key(s) for font stack (order = preference)
_LANG_SCRIPT: dict[str, list[str]] = {
    "en": ["latin"],
    "hi": ["devanagari", "latin"],
    "mr": ["devanagari", "latin"],
    "ta": ["tamil", "latin"],
    "te": ["telugu", "latin"],
    "ur": ["urdu", "latin"],
}


def _font_url(script_key: str) -> str:
    folder, fname = _FONT_FILES[script_key]
    return f"{_NOTO_BASE}/{folder}/{fname}"


def _local_path(script_key: str) -> Path:
    return FONT_DIR / _FONT_FILES[script_key][1]


def ensure_script_font(script_key: str) -> Path | None:
    """Download a Noto TTF into assets/fonts if missing. Returns path or None on failure."""
    if script_key not in _FONT_FILES:
        return None
    dest = _local_path(script_key)
    if dest.exists() and dest.stat().st_size > 10_000:
        return dest

    url = _font_url(script_key)
    with _download_lock:
        if dest.exists() and dest.stat().st_size > 10_000:
            return dest
        try:
            with httpx.Client(timeout=120.0, follow_redirects=True) as client:
                r = client.get(url)
                if r.status_code >= 400:
                    logger.error("Font download failed %s: %s", url, r.status_code)
                    return None
                dest.write_bytes(r.content)
            logger.info("Downloaded font %s -> %s", script_key, dest)
            return dest
        except Exception as e:
            logger.error("Font download error %s: %s", script_key, e)
            return None


def ensure_fonts_for_language(lang: str) -> dict[str, Path]:
    """Ensure all script fonts needed for a UI language are present."""
    keys = _LANG_SCRIPT.get(lang, ["latin"])
    out: dict[str, Path] = {}
    for k in keys:
        p = ensure_script_font(k)
        if p:
            out[k] = p
    return out


def font_paths_for_language(lang: str) -> list[Path]:
    """Ordered list of TTF paths for Pillow (first match used per size via truetype)."""
    paths: list[Path] = []
    for key in _LANG_SCRIPT.get(lang, ["latin"]):
        p = _local_path(key)
        if p.exists():
            paths.append(p)
        else:
            dl = ensure_script_font(key)
            if dl:
                paths.append(dl)
    # Windows fallbacks that cover some Indic if Noto download blocked
    win_extra: list[Path] = []
    if lang in {"hi", "mr"}:
        win_extra.extend(
            Path(p)
            for p in (
                r"C:\Windows\Fonts\Nirmala.ttf",
                r"C:\Windows\Fonts\NirmalaUI.ttf",
                r"C:\Windows\Fonts\Mangal.ttf",
            )
            if Path(p).exists()
        )
    if lang == "ta":
        win_extra.extend(Path(p) for p in (r"C:\Windows\Fonts\Latha.ttf",) if Path(p).exists())
    if lang == "te":
        win_extra.extend(Path(p) for p in (r"C:\Windows\Fonts\Gautami.ttf",) if Path(p).exists())
    if lang == "ur":
        win_extra.extend(Path(p) for p in (r"C:\Windows\Fonts\Urdu Typesetting.ttf",) if Path(p).exists())

    merged: list[Path] = []
    seen: set[str] = set()
    for p in paths + win_extra:
        s = str(p.resolve())
        if s not in seen:
            seen.add(s)
            merged.append(p)
    return merged


def matplotlib_font_family_for_language(lang: str) -> str:
    """Register Noto fonts with matplotlib and return a family name for rcParams."""
    import matplotlib.font_manager as fm

    paths = font_paths_for_language(lang)
    if not paths:
        return "DejaVu Sans"

    try:
        for p in paths:
            try:
                fm.fontManager.addfont(str(p))
            except (ValueError, OSError):
                continue
        prop = fm.FontProperties(fname=str(paths[0]))
        return prop.get_name()
    except Exception as e:
        logger.warning("matplotlib font register failed: %s", e)
        return "DejaVu Sans"


def load_pillow_font(size: int, lang: str) -> Any:
    """Return PIL ImageFont for *lang* with Unicode coverage. Falls back to DejaVu/default."""
    from PIL import ImageFont

    paths = font_paths_for_language(lang)
    for p in paths:
        try:
            return ImageFont.truetype(str(p), size=size)
        except OSError:
            continue
    # Latin fallback
    for p in (
        r"C:\Windows\Fonts\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def shape_rtl_if_urdu(text: str, lang: str) -> str:
    """BiDi + Arabic shaping so Urdu renders correctly in LTR PIL context."""
    if lang != "ur":
        return text
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        shaped = arabic_reshaper.reshape(text)
        return get_display(shaped)
    except ImportError:
        logger.warning("arabic_reshaper/python-bidi not installed; Urdu glyph order may be imperfect")
        return text
