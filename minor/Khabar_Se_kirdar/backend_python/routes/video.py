from fastapi import APIRouter
from pydantic import BaseModel
from services.runway_service import generate_with_runway
from services.local_ai_service import generate_with_local_ai

router = APIRouter(prefix="/video", tags=["Video Generation"])

class VideoRequest(BaseModel):
    text: str


@router.post("/")
def generate_video(request: VideoRequest):

    prompt = request.text

    # 🧠 STEP 1: Try Runway first
    runway_result = generate_with_runway(prompt)

    if runway_result["status"] == "success":
        return {
            "source": "runway",
            "video_url": runway_result["video_url"]
        }

    # 🔁 STEP 2: fallback to local AI
    local_result = generate_with_local_ai(prompt)
    
    return {
    "source": "local_ai",
    "video_url": "/videos/output.mp4"
}