
from fastapi import APIRouter
from pydantic import BaseModel
from services.nlp_service import NLPService

router = APIRouter(prefix="/summarize", tags=["Summarization"])


class NewsRequest(BaseModel):
    text: str


@router.post("/")
def summarize_news(request: NewsRequest):

    summary = NLPService.summarize_news(request.text)

    return {
        "success": True,
        "summary": summary
    }
