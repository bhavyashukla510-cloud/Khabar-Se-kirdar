from fastapi import APIRouter
from pydantic import BaseModel
import requests
import uuid
import os

router = APIRouter(prefix="/story-video", tags=["Story Video"])

OUTPUT_DIR = "outputs/story_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class StoryRequest(BaseModel):
    text: str


@router.post("/")
def generate_story_image(request: StoryRequest):

    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(OUTPUT_DIR, filename)

    prompt = request.text.replace(" ", "%20")

    image_url = f"https://image.pollinations.ai/prompt/{prompt}"

    response = requests.get(image_url)

    with open(filepath, "wb") as f:
        f.write(response.content)

    return {
        "success": True,
        "image_url": f"/outputs/story_images/{filename}"
    }