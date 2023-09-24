from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt

from fastapi import Depends, HTTPException, status, WebSocket, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings


class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(request or websocket)


oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/api/v1/login")  # check this url?


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    password_bytes = bytes(plain_password, "utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password)


def get_password_hash(password: str) -> bytes:
    pw = bytes(password, "utf-8")
    return bcrypt.hashpw(pw, bcrypt.gensalt())


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_by_token(payload: dict = Depends(decode_access_token)) -> str:
    return payload.get("sub")
