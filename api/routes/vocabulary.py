"""Rotas de vocabulário: seed por capítulo."""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_current_user
from api.repositories.seed_repo import SeedInputError, SeedRepository
from api.schemas.vocabulary import SeedChapterRequest, SeedChapterResponse

router = APIRouter()


@router.post("/vocabulary/seed", response_model=SeedChapterResponse)
def seed_chapter(
    payload: SeedChapterRequest,
    user: dict = Depends(get_current_user),
):
    """Registra palavras de um capítulo de forma idempotente."""
    native = (user.get("native_language") or "pt").strip().lower()
    try:
        result = SeedRepository().seed_chapter(
            user_id=user["id"],
            book=payload.book,
            chapter=payload.chapter,
            words=payload.words,
            native_lang=native,
        )
    except SeedInputError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return SeedChapterResponse(**result)
