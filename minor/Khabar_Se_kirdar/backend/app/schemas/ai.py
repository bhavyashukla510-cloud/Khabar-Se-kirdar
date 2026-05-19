from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=20, max_length=50000)
    output_language: str = Field(default="en", pattern="^(en|hi|mr|ta|te|ur)$")


class SummarizeResponse(BaseModel):
    summary: str
    output_language: str


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8000)
    language: str = Field(default="en", pattern="^(en|hi|mr|ta|te|ur)$")


class TTSResponse(BaseModel):
    audio_url: str
    language: str


class STTResponse(BaseModel):
    text: str
    language: str | None = None


class VideoRequest(BaseModel):
    text: str = Field(min_length=20, max_length=50000)
    narration_language: str = Field(default="en", pattern="^(en|hi|mr|ta|te|ur)$")
    subtitle_language: str = Field(default="en", pattern="^(en|hi|mr|ta|te|ur)$")


class VideoResponse(BaseModel):
    video_url: str
    summary: str
    duration_seconds: float


class InfographicRequest(BaseModel):
    text: str = Field(min_length=20, max_length=50000)
    caption_language: str = Field(default="en", pattern="^(en|hi|mr|ta|te|ur)$")


class InfographicResponse(BaseModel):
    image_url: str
    metrics: dict[str, object]
