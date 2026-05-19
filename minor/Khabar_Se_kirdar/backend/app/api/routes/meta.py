from fastapi import APIRouter

from app.services.lang import list_languages

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/languages")
def languages():
    return {"languages": list_languages()}
