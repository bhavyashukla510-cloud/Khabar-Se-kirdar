from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes._history_util import log_history
from app.database import get_db
from app.models.user import User
from app.schemas.ai import SummarizeRequest, SummarizeResponse
from app.services.llm import summarize_article

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(
    body: SummarizeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    summary = summarize_article(body.text, body.output_language)
    log_history(
        db,
        user,
        "summarize",
        "News summary",
        body.output_language,
        body.text,
        summary,
        {},
    )
    return SummarizeResponse(summary=summary, output_language=body.output_language)
