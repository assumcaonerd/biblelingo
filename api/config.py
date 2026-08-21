"""Configuração de runtime e validações de segurança do BibleLingo."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_DEV_SECRET = "dev-secret-change-me-in-production"
DEFAULT_DEV_CORS_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)
PRODUCTION_ENVIRONMENTS = frozenset({"production", "prod"})


@dataclass(frozen=True)
class RuntimeConfig:
    """Configuração imutável derivada das variáveis de ambiente."""

    environment: str
    secret_key: str
    token_expire_hours: int
    cors_origins: tuple[str, ...]

    @property
    def is_production(self) -> bool:
        return self.environment in PRODUCTION_ENVIRONMENTS


def _parse_cors_origins(raw: str | None, environment: str) -> tuple[str, ...]:
    if raw is None:
        return () if environment in PRODUCTION_ENVIRONMENTS else DEFAULT_DEV_CORS_ORIGINS
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


def load_runtime_config() -> RuntimeConfig:
    """Lê a configuração sem fazer efeitos colaterais ou iniciar serviços."""
    environment = os.getenv("BIBLELINGO_ENV", "development").strip().lower()
    raw_hours = os.getenv("BIBLELINGO_TOKEN_HOURS", "72")
    try:
        token_expire_hours = int(raw_hours)
    except ValueError as exc:
        raise ValueError("BIBLELINGO_TOKEN_HOURS deve ser um inteiro") from exc

    return RuntimeConfig(
        environment=environment,
        secret_key=os.getenv("BIBLELINGO_SECRET_KEY", DEFAULT_DEV_SECRET),
        token_expire_hours=token_expire_hours,
        cors_origins=_parse_cors_origins(
            os.getenv("BIBLELINGO_CORS_ORIGINS"), environment
        ),
    )


def validate_runtime_config(config: RuntimeConfig | None = None) -> RuntimeConfig:
    """Valida requisitos de segurança antes de a API aceitar requisições."""
    resolved = config or load_runtime_config()
    errors: list[str] = []

    if resolved.token_expire_hours <= 0:
        errors.append("BIBLELINGO_TOKEN_HOURS deve ser maior que zero")

    if resolved.is_production:
        if resolved.secret_key == DEFAULT_DEV_SECRET:
            errors.append("BIBLELINGO_SECRET_KEY é obrigatório em produção")
        elif len(resolved.secret_key) < 32:
            errors.append("BIBLELINGO_SECRET_KEY deve ter pelo menos 32 caracteres")

        if not resolved.cors_origins:
            errors.append("BIBLELINGO_CORS_ORIGINS é obrigatório em produção")
        elif "*" in resolved.cors_origins:
            errors.append(
                "BIBLELINGO_CORS_ORIGINS não pode conter '*' quando credenciais estão habilitadas"
            )

    if errors:
        raise RuntimeError("Configuração inválida: " + "; ".join(errors))
    return resolved
