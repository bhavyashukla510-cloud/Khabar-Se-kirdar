import json
import os
import re
from typing import Any

from groq import Groq

from app.config import get_settings
from app.services.lang import LANG_INFO

_groq_client: Groq | None = None


def _client() -> Groq | None:
    global _groq_client
    key = get_settings().groq_api_key or os.getenv("GROQ_API_KEY")
    if not key:
        return None
    if _groq_client is None:
        _groq_client = Groq(api_key=key)
    return _groq_client


def summarize_article(text: str, output_language: str) -> str:
    from app.services.cache import summarize_cache_path

    cache_p = summarize_cache_path(output_language, text)
    if cache_p.exists():
        try:
            return cache_p.read_text(encoding="utf-8").strip()
        except OSError:
            pass

    meta = LANG_INFO.get(output_language, LANG_INFO["en"])
    native_name = meta["native"]
    script = meta["script"]
    client = _client()
    system = (
        "You are a multilingual news editor. Produce a concise, factual summary. "
        "Use only the target language in its standard writing system. "
        "Do not Romanize Hindi or other languages. Do not mix English with Hindi (no Hinglish). "
        "Preserve important numbers, dates, and names accurately. "
        "Maximum length: about 120 words."
    )
    user = (
        f"Target language: {native_name} ({script}, ISO-like code {output_language}).\n\n"
        f"News article:\n{text.strip()[:12000]}\n\n"
        "Write the summary only in the target language script."
    )
    if not client:
        return _fallback_summary(text, output_language)

    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.35,
            max_tokens=384,
        )
        out = (r.choices[0].message.content or "").strip()
        if len(out) > 30 and not out.startswith("Summarization failed"):
            try:
                cache_p.write_text(out, encoding="utf-8")
            except OSError:
                pass
        return out
    except Exception as e:
        return f"Summarization failed: {e}"


def translate_for_subtitles(text: str, target_language: str) -> str:
    if target_language == "en":
        return text
    meta = LANG_INFO.get(target_language, LANG_INFO["en"])
    client = _client()
    if not client:
        return text
    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Translate the following news summary into the target language using only "
                        "the standard native script. No Romanization. No Hinglish."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Target: {meta['native']} ({meta['script']}).\n\nText:\n{text}",
                },
            ],
            temperature=0.2,
            max_tokens=520,
        )
        return (r.choices[0].message.content or text).strip()
    except Exception:
        return text


def extract_infographic_json(text: str) -> dict[str, Any]:
    """Use LLM to extract structured metrics; fallback to regex if unavailable."""
    client = _client()
    schema_hint = (
        'Return ONLY valid JSON with keys: "kpis" (list of {label,value,unit}), '
        '"bar" ({labels[], values[]}), "line" ({labels[], values[]}), "notes" (string). '
        "Infer plausible series only when the article clearly implies trends or comparisons."
    )
    if client:
        try:
            r = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You extract quantitative news data for charts."},
                    {"role": "user", "content": f"{schema_hint}\n\nArticle:\n{text[:8000]}"},
                ],
                temperature=0.2,
                max_tokens=720,
            )
            raw = (r.choices[0].message.content or "").strip()
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return _regex_infographic_fallback(text)


def _regex_infographic_fallback(text: str) -> dict[str, Any]:
    percents = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*%", text)]
    big_nums = re.findall(r"\b(\d{1,3}(?:,\d{3})+|\d{2,4})\b", text)
    values = []
    for n in big_nums[:8]:
        try:
            values.append(float(n.replace(",", "")))
        except ValueError:
            continue
    kpis = []
    for i, p in enumerate(percents[:4]):
        kpis.append({"label": f"Rate {i+1}", "value": str(p), "unit": "%"})
    if not kpis and values:
        kpis = [{"label": "Figure 1", "value": str(values[0]), "unit": ""}]
    labels = [f"M{i+1}" for i in range(min(5, len(values)))]
    vals = values[: len(labels)] or [0, 0, 0]
    if len(vals) < 2:
        vals = [1, 2, 3, 4, 5]
        labels = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    return {
        "kpis": kpis or [{"label": "Highlight", "value": "—", "unit": ""}],
        "bar": {"labels": labels, "values": vals},
        "line": {"labels": labels, "values": vals},
        "notes": "Heuristic extraction from text.",
    }


def _fallback_summary(text: str, output_language: str) -> str:
    snippet = text.strip()[:400].replace("\n", " ")
    return (
        f"[Configure GROQ_API_KEY] Preview extract ({output_language}): {snippet}..."
    )
