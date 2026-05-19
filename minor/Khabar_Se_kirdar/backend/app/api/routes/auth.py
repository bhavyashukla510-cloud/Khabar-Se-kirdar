from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == str(payload.email).lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=str(payload.email).lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name or "",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(payload.email).lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token, expires = create_access_token(user.email, remember_me=payload.remember_me)
    return Token(access_token=token, expires_in=expires)


@router.post("/logout")
def logout():
    return {"ok": True, "detail": "Discard the access token on the client."}


@router.get("/me", response_model=UserOut)
def read_me(user: User = Depends(get_current_user)):
    return user


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    """UI hook: password reset email is not sent in this reference deployment."""
    return {
        "ok": True,
        "detail": "If an account exists for this email, reset instructions would be sent.",
    }
