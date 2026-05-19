from fastapi import APIRouter
from pydantic import BaseModel
from services.nlp_service import NLPService

router = APIRouter(prefix="/translate", tags=["Translation"])


class TranslateRequest(BaseModel):
    text: str
    language: str


@router.post("/")
def translate(request: TranslateRequest):

    translated_text = NLPService.translate_text(
        request.text,
        request.language
    )

    return {
        "success": True,
        "translated_text": translated_text
    }
