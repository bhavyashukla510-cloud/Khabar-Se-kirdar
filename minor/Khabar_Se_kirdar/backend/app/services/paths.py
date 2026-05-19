"""Shared paths under `backend/outputs` for static URLs."""

from pathlib import Path

OUTPUTS_ROOT = Path(__file__).resolve().parent.parent.parent / "outputs"


def static_url_for_output_file(path: Path) -> str:
    rel = path.resolve().relative_to(OUTPUTS_ROOT.resolve())
    return "/static/" + rel.as_posix()
