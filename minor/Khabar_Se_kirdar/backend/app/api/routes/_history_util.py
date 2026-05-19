import json

from sqlalchemy.orm import Session

from app.models.history import HistoryItem
from app.models.user import User


def log_history(
    db: Session,
    user: User,
    kind: str,
    title: str,
    language: str,
    input_preview: str,
    output_preview: str,
    meta: dict | None = None,
) -> None:
    item = HistoryItem(
        user_id=user.id,
        kind=kind,
        title=title[:500],
        language=language,
        input_preview=input_preview[:4000],
        output_preview=output_preview[:4000],
        meta_json=json.dumps(meta or {}),
    )
    db.add(item)
    db.commit()
