from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes._history_util import log_history
from app.database import get_db
from app.models.user import User
from app.schemas.ai import VideoRequest, VideoResponse
from app.services.paths import static_url_for_output_file
from app.services.video import render_news_video

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/video", response_model=VideoResponse)
def video(
    body: VideoRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        path, summary, duration = render_news_video(
            body.text,
            body.narration_language,
            body.subtitle_language,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    url = static_url_for_output_file(path)
    log_history(
        db,
        user,
        "video",
        "AI news video",
        body.narration_language,
        body.text[:2000],
        summary[:2000],
        {"subtitle_language": body.subtitle_language, "video_url": url},
    )
    return VideoResponse(video_url=url, summary=summary, duration_seconds=duration)
