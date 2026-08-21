"""Dependências compartilhadas da API.

A autenticação será adicionada posteriormente. Enquanto isso, X-User-ID permite
que os testes e clientes antecipem o isolamento por usuário sem alterar as rotas.
"""

from __future__ import annotations

from fastapi import Header

from api.database import DEFAULT_USER_ID


def get_user_id(x_user_id: str | None = Header(default=None)) -> str:
    """Retorna um identificador estável para o escopo de dados da requisição."""
    value = (x_user_id or DEFAULT_USER_ID).strip()
    if not value:
        return DEFAULT_USER_ID
    return value[:128]
