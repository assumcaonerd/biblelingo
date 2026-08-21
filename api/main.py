"""Aplicação FastAPI do BibleLingo.

Como rodar:
    uvicorn api.main:app --reload

Documentação interativa:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from api.database import initialize_database
from api.routes import api_router

app = FastAPI(
    title="BibleLingo API",
    description=(
        "API do BibleLingo – aprender inglês lendo e ouvindo a Bíblia. "
        "O domínio de regras (XP, streak, vocabulário, quiz) vive em app/domain/ "
        "e é compartilhado com o CLI."
    ),
    version="0.2.0",
)

app.include_router(api_router)


@app.on_event("startup")
def startup() -> None:
    """Garante que as tabelas existam antes da primeira requisição."""
    initialize_database()


@app.get("/")
def root():
    return {
        "service": "biblelingo",
        "docs": "/docs",
        "health": "/health",
        "progress": "/v1/progress",
        "chapters": "/v1/chapters",
        "review_answer": "/v1/reviews/answer",
    }
