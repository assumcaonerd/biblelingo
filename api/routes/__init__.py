"""Rotas da API."""

from fastapi import APIRouter

from .chapters import router as chapters_router
from .health import router as health_router
from .progress import router as progress_router
from .reviews import router as reviews_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(progress_router, prefix="/v1", tags=["progress"])
api_router.include_router(chapters_router, prefix="/v1", tags=["content"])
api_router.include_router(reviews_router, prefix="/v1", tags=["reviews"])
