"""Rotas de progresso (XP, nível, streak)."""

from fastapi import APIRouter, Depends

from api.dependencies import get_user_id
from api.repositories.progress_repo import ProgressRepository
from api.schemas.progress import LevelProgress, ProgressResponse

router = APIRouter()


def _to_response(progress) -> ProgressResponse:
    lp = progress.level_progress()
    return ProgressResponse(
        xp=progress.xp,
        level=progress.level,
        current_streak=progress.current_streak,
        longest_streak=progress.longest_streak,
        last_activity_date=progress.last_activity_date,
        streak_bonus=progress.get_streak_bonus(),
        level_progress=LevelProgress(**lp),
    )


@router.get("/progress", response_model=ProgressResponse)
def get_progress(user_id: str = Depends(get_user_id)):
    """Retorna o progresso atual do usuário."""
    repo = ProgressRepository()
    progress = repo.load(user_id=user_id)
    return _to_response(progress)
