from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from starlette import status
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.core.config import settings


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(request or websocket)


oauth2_scheme = CustomOAuth2PasswordBearer(
    tokenUrl="http://127.0.0.1:8000/api/v1/login"
)  # check this url?


def create_jwt(data: dict, token_type: str = "access") -> str:
    to_encode = data.copy()
    if token_type == "access":
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    elif token_type == "refresh":
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    else:
        raise ValueError("Incorrect JWT type (Should be access or refresh)")
    expire_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire_at})
    encoded_jwt_token = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt_token


def decode_jwt(token: str = Depends(oauth2_scheme)) -> dict:
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


def get_user_by_token(payload: dict = Depends(decode_jwt)) -> str:
    return payload.get("sub")
