from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, remember_me: bool = False) -> tuple[str, int]:
    settings = get_settings()
    expire_minutes = (
        settings.access_token_expire_minutes_remember if remember_me else settings.access_token_expire_minutes
    )
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    token = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return token, int(expire_minutes * 60)


def decode_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if isinstance(sub, str):
            return sub
    except JWTError:
        return None
    return None
