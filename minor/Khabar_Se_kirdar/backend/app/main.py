from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, history, infographic, meta, stt, summarize, tts, video
from app.config import get_settings
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    root = Path(__file__).resolve().parent.parent
    for sub in ("audio", "video", "infographics", "tmp", "cache"):
        (root / "outputs" / sub).mkdir(parents=True, exist_ok=True)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="News Intelligence Platform", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    outputs = Path(__file__).resolve().parent.parent / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(outputs)), name="static")

    app.include_router(auth.router)
    app.include_router(meta.router)
    app.include_router(history.router)
    app.include_router(summarize.router)
    app.include_router(tts.router)
    app.include_router(stt.router)
    app.include_router(video.router)
    app.include_router(infographic.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
