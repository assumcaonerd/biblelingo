"""Endpoint agregado do dashboard."""

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_user_id
from api.repositories.dashboard_repo import DashboardRepository
from api.schemas.dashboard import DashboardResponse

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    user_id: str = Depends(get_user_id),
    daily_goal: int = Query(default=5, ge=1, le=50),
):
    """Resumo de XP, vocabulário, meta diária e atividade recente."""
    data = DashboardRepository().summary(
        user_id=user_id,
        daily_goal=daily_goal,
    )
    return DashboardResponse(**data)
