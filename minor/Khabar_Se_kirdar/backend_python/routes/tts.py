from fastapi import APIRouter
from pydantic import BaseModel
from gtts import gTTS
import uuid
import os

from services.nlp_service import NLPService

router = APIRouter(prefix="/tts", tags=["Text To Speech"])

OUTPUT_DIR = "outputs/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class TTSRequest(BaseModel):
    text: str
    language: str = "en"   


@router.post("/")
def text_to_speech(request: TTSRequest):

    text = request.text
    lang = request.language

    if lang != "en":
        text = NLPService.translate_text(request.text, lang)

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)

   
    tts = gTTS(
        text=text,
        lang=lang,
        tld="co.in" if lang == "hi" else "com"
    )

    tts.save(filepath)

    return {
        "success": True,
        "audio_url": f"/outputs/audio/{filename}",
        "language_used": lang,
        "final_text": text
    }