import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes._history_util import log_history
from app.database import get_db
from app.models.user import User
from app.schemas.ai import STTResponse
from app.services.stt import transcribe_file

router = APIRouter(prefix="/ai", tags=["ai"])

TMP = Path(__file__).resolve().parent.parent.parent.parent / "outputs" / "tmp"
TMP.mkdir(parents=True, exist_ok=True)


@router.post("/stt", response_model=STTResponse)
def stt_endpoint(
    file: UploadFile = File(...),
    language: str = Form(default="en"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    language = (language or "en").strip().lower()
    if len(language) > 2:
        language = language[:2]
    if language not in {"en", "hi", "mr", "ta", "te", "ur"}:
        raise HTTPException(status_code=400, detail="Unsupported language")
    suffix = Path(file.filename or "upload").suffix or ".wav"
    dest = TMP / f"{uuid.uuid4().hex}{suffix}"
    data = file.file.read()
    dest.write_bytes(data)
    try:
        text = transcribe_file(dest, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        try:
            dest.unlink()
        except OSError:
            pass

    log_history(
        db,
        user,
        "stt",
        "Speech to text",
        language,
        file.filename or "audio",
        text[:4000],
        {},
    )
    return STTResponse(text=text, language=language)
