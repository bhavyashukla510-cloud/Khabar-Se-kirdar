from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

# Load `backend/.env` first, then repo-root `Khabar_Se_kirdar/.env` with override so a real
# GROQ_API_KEY in the project root is not masked by a placeholder left in `backend/.env`.
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env", override=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    secret_key: str = "dev-insecure-change-in-production"
    groq_api_key: str | None = None

    @field_validator("groq_api_key", mode="before")
    @classmethod
    def strip_groq_key(cls, v: object) -> object:
        if isinstance(v, str):
            s = v.strip()
            return s or None
        return v
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'app.db'}"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    access_token_expire_minutes: int = 60 * 24
    access_token_expire_minutes_remember: int = 60 * 24 * 14

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
