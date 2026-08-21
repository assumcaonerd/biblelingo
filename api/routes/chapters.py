"""Rotas de conteúdo bíblico."""

from fastapi import APIRouter, HTTPException

from api.repositories.content_repo import ContentRepository
from api.schemas.content import ChapterOut

router = APIRouter()


@router.get("/chapters", response_model=list[str])
def list_chapters():
    """Lista livros disponíveis."""
    repo = ContentRepository()
    return repo.list_available_books()


@router.get("/chapters/{book}/{chapter}", response_model=ChapterOut)
def get_chapter(book: str, chapter: int):
    """Retorna os versículos de um capítulo."""
    if chapter < 1:
        raise HTTPException(status_code=400, detail="chapter must be >= 1")

    repo = ContentRepository()
    try:
        data = repo.get_chapter(book, chapter)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not data["verses"]:
        raise HTTPException(
            status_code=404,
            detail=f"No verses found for {book} chapter {chapter}",
        )

    return ChapterOut(**data)
