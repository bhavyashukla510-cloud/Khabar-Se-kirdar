from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes._history_util import log_history
from app.database import get_db
from app.models.user import User
from app.schemas.ai import InfographicRequest, InfographicResponse
from app.services.infographic import build_infographic

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/infographic", response_model=InfographicResponse)
def infographic(
    body: InfographicRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        url, metrics = build_infographic(body.text, body.caption_language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    log_history(
        db,
        user,
        "infographic",
        "Infographic",
        body.caption_language,
        body.text[:2000],
        url,
        {"metrics": metrics},
    )
    return InfographicResponse(image_url=url, metrics=metrics)
