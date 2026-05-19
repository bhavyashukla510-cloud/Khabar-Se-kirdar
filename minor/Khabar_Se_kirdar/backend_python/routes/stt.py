from fastapi import APIRouter, UploadFile, File
import speech_recognition as sr
from pydub import AudioSegment
import os
import uuid

router = APIRouter(prefix="/stt", tags=["Speech To Text"])

TEMP_DIR = "outputs/audio"
os.makedirs(TEMP_DIR, exist_ok=True)


@router.post("/")
async def speech_to_text(file: UploadFile = File(...)):

    temp_file = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.wav")

    with open(temp_file, "wb") as f:
        f.write(await file.read())

    recognizer = sr.Recognizer()

    with sr.AudioFile(temp_file) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)

        return {
            "success": True,
            "text": text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
