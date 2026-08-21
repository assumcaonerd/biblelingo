"""Health checks públicos da API."""

from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException

from api.config import validate_runtime_config
from api.database import connect

router = APIRouter()


@router.get("/health")
def health():
    """Liveness simples, útil para saber se o processo responde."""
    return {"status": "ok", "service": "biblelingo"}


@router.get("/health/ready")
def readiness():
    """Readiness sem dados sensíveis: configuração válida e banco acessível."""
    try:
        config = validate_runtime_config()
        with connect() as connection:
            connection.execute("SELECT 1").fetchone()
    except (RuntimeError, sqlite3.Error) as exc:
        raise HTTPException(status_code=503, detail="service not ready") from exc

    return {
        "status": "ready",
        "service": "biblelingo",
        "environment": config.environment,
    }
