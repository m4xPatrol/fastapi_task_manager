from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.schemas.user import UserModel, UserCreate
from app.core.security import get_password_hash, create_access_token, get_user_by_token, verify_password
from app.db.database import get_session
from app.db.models.user import User

from app.db.crud.user import user_crud

router = APIRouter()


@router.post("/register", response_model=UserModel)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    try:
        user_db = await user_crud.add_user(db, user)
        return user_db
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email was already registered.")


@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_session)):
    user_db = await user_crud.get_user(db, form_data.username)
    if not user_db or not verify_password(form_data.password, user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect.",
                            headers={"WWW-Authenticate": "Bearer"})
    jwt_token = create_access_token({"sub": user_db.username})
    return {"access_token": jwt_token, "token_type": "bearer"}


@router.get("/about_me", response_model=UserModel)
async def read_user(db: AsyncSession = Depends(get_session), username: str = Depends(get_user_by_token)):
    user_db = await user_crud.get_user(db, username)
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_db
