import logging
import uuid
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.services.cache import infographic_cache_paths, read_json, write_json
from app.services.fonts import matplotlib_font_family_for_language
from app.services.llm import extract_infographic_json

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs" / "infographics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_infographic(text: str, caption_language: str) -> tuple[str, dict[str, Any]]:
    caption_language = (caption_language or "en").strip().lower()[:2]

    cache_png, cache_json = infographic_cache_paths(caption_language, text)
    if cache_png.exists() and cache_png.stat().st_size > 500:
        metrics = read_json(cache_json)
        if isinstance(metrics, dict) and metrics:
            logger.info("infographic cache hit %s", cache_png.name)
            return f"/static/cache/{cache_png.name}", metrics

    data = extract_infographic_json(text)
    kpis = data.get("kpis") or []
    bar = data.get("bar") or {"labels": [], "values": []}
    line = data.get("line") or {"labels": [], "values": []}

    fname = f"{uuid.uuid4().hex}.png"
    fpath = OUTPUT_DIR / fname

    family = matplotlib_font_family_for_language(caption_language)
    prev_family = plt.rcParams.get("font.family")
    prev_sans = plt.rcParams.get("font.sans-serif")
    try:
        plt.rcParams["font.family"] = family
        plt.rcParams["font.sans-serif"] = [family, "DejaVu Sans", "sans-serif"]

        fig = plt.figure(figsize=(11, 6.5), facecolor="#0f172a")
        fig.patch.set_facecolor("#0f172a")

        ax_title = fig.add_axes([0.05, 0.88, 0.9, 0.08])
        ax_title.axis("off")
        ax_title.text(
            0.0,
            0.5,
            f"News intelligence · {caption_language.upper()}",
            color="#e2e8f0",
            fontsize=16,
            weight="bold",
            va="center",
            fontfamily=family,
        )

        n_kpi = min(4, max(1, len(kpis)))
        for i in range(n_kpi):
            k = kpis[i] if i < len(kpis) else {"label": "—", "value": "—", "unit": ""}
            ax = fig.add_axes([0.05 + i * 0.235, 0.62, 0.21, 0.2])
            ax.set_facecolor("#1e293b")
            ax.axis("off")
            ax.text(
                0.5,
                0.65,
                str(k.get("label", "")),
                ha="center",
                va="center",
                color="#94a3b8",
                fontsize=10,
                fontfamily=family,
            )
            unit = k.get("unit") or ""
            val = f"{k.get('value', '')}{unit}"
            ax.text(
                0.5,
                0.35,
                val,
                ha="center",
                va="center",
                color="#38bdf8",
                fontsize=18,
                weight="bold",
                fontfamily=family,
            )

        ax_bar = fig.add_axes([0.05, 0.08, 0.42, 0.48])
        ax_bar.set_facecolor("#1e293b")
        labels = bar.get("labels") or ["A", "B", "C"]
        values = bar.get("values") or [1, 2, 3]
        ax_bar.bar([str(x) for x in labels], values, color="#22c55e")
        ax_bar.tick_params(colors="#cbd5e1", labelsize=9)
        for tick in ax_bar.get_xticklabels():
            tick.set_fontfamily(family)
        ax_bar.spines[:].set_color("#334155")
        ax_bar.set_title("Comparison", color="#e2e8f0", fontsize=11, fontfamily=family)

        ax_line = fig.add_axes([0.53, 0.08, 0.42, 0.48])
        ax_line.set_facecolor("#1e293b")
        ll = line.get("labels") or labels
        lv = line.get("values") or values
        ax_line.plot([str(x) for x in ll], lv, color="#a855f7", marker="o", linewidth=2)
        ax_line.tick_params(colors="#cbd5e1", labelsize=9)
        for tick in ax_line.get_xticklabels():
            tick.set_fontfamily(family)
        ax_line.spines[:].set_color("#334155")
        ax_line.set_title("Trend", color="#e2e8f0", fontsize=11, fontfamily=family)

        fig.savefig(fpath, dpi=110, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close(fig)
    finally:
        if prev_family is not None:
            plt.rcParams["font.family"] = prev_family
        if prev_sans is not None:
            plt.rcParams["font.sans-serif"] = prev_sans

    url = f"/static/infographics/{fname}"
    try:
        import shutil

        shutil.copy2(fpath, cache_png)
        write_json(cache_json, data)
    except Exception as e:
        logger.warning("infographic cache write failed: %s", e)

    return url, data
