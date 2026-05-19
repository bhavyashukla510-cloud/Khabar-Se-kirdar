from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.summarize import router as summarize_router
from routes.tts import router as tts_router
from routes.stt import router as stt_router
from routes.translate import router as translate_router
from routes.infographics import router as infographic_router
from routes.video import router as video_router
from routes.story_video import router as story_video_router

app = FastAPI(title="Khabar Se Kirdar API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

app.mount(
    "/videos",
    StaticFiles(directory="backend-python/outputs/video"),
    name="videos"
)
app.include_router(summarize_router)
app.include_router(tts_router)
app.include_router(stt_router)
app.include_router(translate_router)
app.include_router(infographic_router)
app.include_router(video_router)
app.include_router(story_video_router)

@app.get("/")
def home():
    return {"message": "Khabar-Se-Kirdar Python Backend Running"}