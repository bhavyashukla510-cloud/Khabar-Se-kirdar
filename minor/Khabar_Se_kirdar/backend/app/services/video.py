import json
import logging
import shutil
import textwrap
import uuid
from pathlib import Path

from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw

from app.services.cache import read_json, video_cache_paths, write_json
from app.services.fonts import load_pillow_font, shape_rtl_if_urdu
from app.services.llm import summarize_article, translate_for_subtitles
from app.services.tts import run_tts

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs" / "video"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1280, 720


def _wrap(text: str, width: int) -> str:
    """Textwrap with width tuned for mixed Indic / Latin (glyphs wider than monospace)."""
    if not text.strip():
        return ""
    return textwrap.fill(text, width=width, break_long_words=False, replace_whitespace=False)


def _draw_avatar(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    r = 55
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#38bdf8", width=4)
    draw.line([cx, cy + r, cx, cy + r + 120], fill="#38bdf8", width=5)
    draw.line([cx, cy + r + 40, cx - 60, cy + r + 90], fill="#38bdf8", width=5)
    draw.line([cx, cy + r + 40, cx + 60, cy + r + 90], fill="#38bdf8", width=5)
    draw.line([cx, cy + r + 120, cx - 50, cy + r + 200], fill="#38bdf8", width=5)
    draw.line([cx, cy + r + 120, cx + 50, cy + r + 200], fill="#38bdf8", width=5)


def _frame(
    scene_text: str,
    subtitle: str,
    chart_color: tuple[int, int, int],
    body_lang: str,
    sub_lang: str,
) -> Image.Image:
    img = Image.new("RGB", (W, H), "#0b1224")
    draw = ImageDraw.Draw(img)

    title_font = load_pillow_font(26, body_lang)
    body_font = load_pillow_font(30, body_lang)
    sub_font = load_pillow_font(26, sub_lang)

    _draw_avatar(draw, 200, 220)

    draw.rectangle([420, 80, W - 60, H - 160], outline="#1e293b", width=2)
    draw.text((440, 100), "Briefing", fill="#94a3b8", font=title_font)

    body_display = shape_rtl_if_urdu(scene_text, body_lang)
    wrapped = _wrap(body_display, 34)
    draw.multiline_text((440, 140), wrapped, fill="#e2e8f0", font=body_font, spacing=8)

    bx, by, bw, bh = 440, H - 260, W - 500, 70
    draw.rectangle([bx, by, bx + bw, by + bh], fill="#111827", outline="#334155")
    for i in range(5):
        h = 20 + (i * 17) % 50
        x0 = bx + 20 + i * ((bw - 40) // 5)
        w = (bw - 80) // 6
        draw.rectangle([x0, by + bh - h, x0 + w, by + bh], fill=chart_color)

    sub_display = shape_rtl_if_urdu(subtitle, sub_lang)
    sub_wrapped = _wrap(sub_display, 52)
    draw.rectangle([40, H - 120, W - 40, H - 40], fill="#020617", outline="#334155")
    draw.multiline_text((60, H - 112), sub_wrapped, fill="#f8fafc", font=sub_font, spacing=4)
    return img


def render_news_video(
    article: str,
    narration_language: str,
    subtitle_language: str,
) -> tuple[Path, str, float]:
    narration_language = (narration_language or "en").strip().lower()[:2]
    subtitle_language = (subtitle_language or "en").strip().lower()[:2]

    cache_mp4, cache_meta = video_cache_paths(article, narration_language, subtitle_language)
    if cache_mp4.exists() and cache_mp4.stat().st_size > 10_000:
        meta = read_json(cache_meta) or {}
        summary = str(meta.get("summary") or "")
        duration = float(meta.get("duration") or 0)
        if summary and duration > 0:
            logger.info("video cache hit %s", cache_mp4.name)
            return cache_mp4, summary, duration

    summary = summarize_article(article, narration_language)
    subtitles = translate_for_subtitles(summary, subtitle_language)

    audio_path = run_tts(summary, narration_language)
    audio_clip = AudioFileClip(str(audio_path))
    duration = float(audio_clip.duration or 1.0)

    parts = [p.strip() for p in summary.replace("।", ".").replace("?", ".").split(".") if p.strip()]
    if len(parts) < 2:
        parts = textwrap.wrap(summary, width=100, break_long_words=False) or [summary]
    n = len(parts)
    per = max(duration / n, 1.2)

    sub_parts = [p.strip() for p in subtitles.replace("۔", ".").replace("?", ".").split(".") if p.strip()]
    if len(sub_parts) < n:
        sub_parts = sub_parts + [subtitles[-200:]] * (n - len(sub_parts))

    colors = [(56, 189, 248), (34, 197, 94), (168, 85, 247), (250, 204, 21)]

    clips = []
    temp_pngs: list[Path] = []
    for i, chunk in enumerate(parts):
        sub_line = sub_parts[i] if i < len(sub_parts) else subtitles[:200]
        frame = _frame(chunk, sub_line[:400], colors[i % len(colors)], narration_language, subtitle_language)
        p = OUTPUT_DIR / f"frame_{uuid.uuid4().hex}.png"
        frame.save(str(p))
        temp_pngs.append(p)
        clips.append(ImageClip(str(p)).set_duration(per))

    video_only = concatenate_videoclips(clips, method="compose")
    video_only = video_only.set_audio(audio_clip)

    out = OUTPUT_DIR / f"news_{uuid.uuid4().hex}.mp4"
    video_only.write_videofile(
        str(out),
        fps=20,
        codec="libx264",
        audio_codec="aac",
        preset="veryfast",
        audio_bitrate="96k",
        threads=4,
        ffmpeg_params=["-movflags", "+faststart", "-b:v", "1800k"],
        logger=None,
    )

    audio_clip.close()
    video_only.close()
    for c in clips:
        try:
            c.close()
        except Exception:
            pass
    for p in temp_pngs:
        try:
            p.unlink()
        except OSError:
            pass

    try:
        shutil.copy2(out, cache_mp4)
        write_json(cache_meta, {"summary": summary, "duration": duration})
    except Exception as e:
        logger.warning("video cache write failed: %s", e)

    return out, summary, duration
