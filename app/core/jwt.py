from datetime import datetime, timedelta
import secrets
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from starlette import status
from starlette.requests import Request
from starlette.websockets import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.crud.refresh_token import refresh_token_crud
from app.db.crud.user import user_crud
from app.db.models.refresh_token import RefreshToken


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(request or websocket)


oauth2_scheme = CustomOAuth2PasswordBearer(
    tokenUrl="http://127.0.0.1:8000/api/v1/login"
)  # check this url?


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_access_token = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_access_token


def decode_access_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_by_token(payload: dict = Depends(decode_access_token)) -> str:
    return payload.get("sub")


async def create_refresh_token(
    db: AsyncSession, user_id: int, refresh_token_value: str | None = None
) -> str:
    if refresh_token_value is None:
        refresh_token_value = secrets.token_hex(64)
    expire = datetime.utcnow() + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    await refresh_token_crud.create_refresh_token(
        db, user_id, expire, refresh_token_value
    )
    return refresh_token_value


async def update_refresh_token(db: AsyncSession, refresh_token: RefreshToken) -> str:
    new_refresh_token_value = secrets.token_hex(64)
    await refresh_token_crud.update_refresh_token(
        db, refresh_token, new_refresh_token_value
    )
    return new_refresh_token_value


def get_refresh_token_settings(
    refresh_token: str, expired: bool = False
) -> dict[str, Any]:
    base_cookie = {
        "key": "refreshToken",
        "httponly": True,
        "samesite": "none",
        "secure": True,
        # "domain": settings.SITE_DOMAIN,
    }
    if expired:
        return base_cookie

    return {
        **base_cookie,
        "value": refresh_token,
        "max_age": settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    }


async def valid_refresh_token(db: AsyncSession, refresh_token: str) -> RefreshToken:
    db_refresh_token = await refresh_token_crud.get_refresh_token(db, refresh_token)

    if not db_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not _is_valid_refresh_token(db_refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return db_refresh_token


def _is_valid_refresh_token(db_refresh_token: RefreshToken) -> bool:
    return datetime.utcnow() <= db_refresh_token.expires_at


async def valid_refresh_token_user(
    db: AsyncSession,
    refresh_token: RefreshToken = Depends(valid_refresh_token),
) -> str:
    user = await user_crud.get_user_by_id(db, refresh_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user.username
