"""Endpoints de revisão e sessão de estudo."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.languages import SUPPORTED_NATIVE_LANGUAGES

from api.dependencies import get_current_user, get_user_id
from api.repositories.review_repo import (
    ReviewConflictError,
    ReviewInputError,
    ReviewRepository,
)
from api.schemas.review import (
    DueReviewsResponse,
    ReviewAnswerRequest,
    ReviewAnswerResponse,
    StudySessionRequest,
    StudySessionResponse,
)

router = APIRouter()


def _resolve_lang(user: dict, native_lang: str | None) -> str:
    lang = (native_lang or user.get("native_language") or "pt").strip().lower()
    if lang not in SUPPORTED_NATIVE_LANGUAGES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported native language: {lang}",
        )
    return lang


@router.get("/reviews/due", response_model=DueReviewsResponse)
def list_due_reviews(
    limit: int = Query(default=20, ge=1, le=50),
    native_lang: str | None = Query(default=None, min_length=2, max_length=8),
    user: dict = Depends(get_current_user),
):
    """Somente leitura: palavras vencidas, sem emitir perguntas nem gravar estado."""
    lang = _resolve_lang(user, native_lang)
    result = ReviewRepository().list_due(
        user_id=user["id"],
        native_lang=lang,
        limit=limit,
    )
    return DueReviewsResponse(**result)


@router.post("/study-sessions", response_model=StudySessionResponse)
def create_study_session(
    payload: StudySessionRequest,
    user: dict = Depends(get_current_user),
):
    """Emite question_ids para prática (side effect explícito)."""
    lang = _resolve_lang(user, payload.native_lang)
    result = ReviewRepository().create_session(
        user_id=user["id"],
        native_lang=lang,
        limit=payload.limit,
    )
    return StudySessionResponse(**result)


@router.post("/reviews/answer", response_model=ReviewAnswerResponse)
def answer_review(
    payload: ReviewAnswerRequest,
    user_id: str = Depends(get_user_id),
):
    """Corrige resposta apenas para question_id emitido ao usuário."""
    try:
        return ReviewRepository().answer(
            user_id=user_id,
            question_id=payload.question_id,
            selected=payload.selected,
            idempotency_key=payload.idempotency_key,
        )
    except ReviewConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ReviewInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
