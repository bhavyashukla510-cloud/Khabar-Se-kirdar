from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes._history_util import log_history
from app.database import get_db
from app.models.user import User
from app.schemas.ai import TTSRequest, TTSResponse
from app.services.tts import synthesize_to_file

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/tts", response_model=TTSResponse)
async def tts_endpoint(
    body: TTSRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        path = await synthesize_to_file(body.text, body.language)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS failed: {e}") from e
    url = f"/static/audio/{path.name}"
    log_history(
        db,
        user,
        "tts",
        "Text to speech",
        body.language,
        body.text[:2000],
        url,
        {},
    )
    return TTSResponse(audio_url=url, language=body.language)
