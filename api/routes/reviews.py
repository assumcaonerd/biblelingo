"""Endpoint de resposta de revisão."""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_user_id
from api.repositories.review_repo import ReviewInputError, ReviewRepository
from api.schemas.review import ReviewAnswerRequest, ReviewAnswerResponse

router = APIRouter()


@router.post("/reviews/answer", response_model=ReviewAnswerResponse)
def answer_review(
    payload: ReviewAnswerRequest,
    user_id: str = Depends(get_user_id),
):
    """Corrige uma resposta e persiste revisão + XP atomicamente."""
    try:
        return ReviewRepository().answer(
            user_id=user_id,
            word=payload.word,
            selected=payload.selected,
            native_lang=payload.native_lang,
            idempotency_key=payload.idempotency_key,
        )
    except ReviewInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
