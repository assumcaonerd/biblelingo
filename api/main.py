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
        "Autenticação por JWT. O domínio de regras vive em app/domain/."
    ),
    version="0.3.0",
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
        "version": "0.3.0",
        "docs": "/docs",
        "health": "/health",
        "auth": {
            "register": "POST /v1/auth/register",
            "login": "POST /v1/auth/login",
            "me": "GET /v1/me",
        },
        "progress": "GET /v1/progress",
        "chapters": "GET /v1/chapters",
        "review_answer": "POST /v1/reviews/answer",
    }
