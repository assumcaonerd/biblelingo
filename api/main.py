"""Aplicação FastAPI do BibleLingo.

Como rodar:
    uvicorn api.main:app --reload

Documentação interativa:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import load_runtime_config, validate_runtime_config
from api.database import initialize_database
from api.routes import api_router

runtime_config = load_runtime_config()

app = FastAPI(
    title="BibleLingo API",
    description=(
        "API do BibleLingo – aprender inglês lendo e ouvindo a Bíblia. "
        "Autenticação por JWT. O domínio de regras vive em app/domain/."
    ),
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(runtime_config.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
)

app.include_router(api_router)


@app.on_event("startup")
def startup() -> None:
    """Valida a configuração e garante as tabelas antes das requisições."""
    validate_runtime_config()
    initialize_database()


@app.get("/")
def root():
    return {
        "service": "biblelingo",
        "version": "0.4.0",
        "docs": "/docs",
        "health": "/health",
        "ready": "/health/ready",
        "auth": {
            "register": "POST /v1/auth/register",
            "login": "POST /v1/auth/login",
            "me": "GET /v1/me",
        },
        "progress": "GET /v1/progress",
        "dashboard": "GET /v1/dashboard",
        "chapters": "GET /v1/chapters",
        "review_answer": "POST /v1/reviews/answer",
    }
