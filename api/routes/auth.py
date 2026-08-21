"""Rotas de autenticação: registro, login e perfil."""

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth import create_access_token
from api.dependencies import get_current_user
from api.repositories.user_repo import UserRepository
from api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    """Cria conta e devolve token de acesso."""
    repo = UserRepository()
    try:
        user = repo.create(
            email=str(payload.email),
            password=payload.password,
            native_language=payload.native_language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    token = create_access_token(user_id=user["id"], email=user["email"])
    return TokenResponse(
        access_token=token,
        user=UserOut(**user),
    )


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    """Autentica e devolve token de acesso."""
    user = UserRepository().authenticate(str(payload.email), payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(user_id=user["id"], email=user["email"])
    return TokenResponse(
        access_token=token,
        user=UserOut(**user),
    )


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    """Retorna o perfil do usuário autenticado."""
    return UserOut(**user)
