"""Autenticação: hash de senha e tokens JWT."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from api.config import load_runtime_config, validate_runtime_config

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    user_id: str, email: str, extra: dict[str, Any] | None = None
) -> str:
    config = validate_runtime_config()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=config.token_expire_hours)
    payload: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": now,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, config.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    config = validate_runtime_config()
    return jwt.decode(token, config.secret_key, algorithms=[ALGORITHM])


def current_runtime_environment() -> str:
    """Retorna o ambiente atual sem expor o segredo ou outras credenciais."""
    return load_runtime_config().environment
