from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.history import HistoryItem
from app.models.user import User

router = APIRouter(prefix="/history", tags=["history"])


class HistoryOut(BaseModel):
    id: int
    kind: str
    title: str
    language: str
    input_preview: str
    output_preview: str
    created_at: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[HistoryOut])
def list_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = 50,
):
    rows = (
        db.query(HistoryItem)
        .filter(HistoryItem.user_id == user.id)
        .order_by(HistoryItem.created_at.desc())
        .limit(min(limit, 200))
        .all()
    )
    return [
        HistoryOut(
            id=r.id,
            kind=r.kind,
            title=r.title,
            language=r.language,
            input_preview=r.input_preview,
            output_preview=r.output_preview,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in rows
    ]
