from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.schemas.user import UserModel, UserInputModel
from app.core.security import get_password_hash, create_access_token, get_user_by_token, verify_password
from app.db.database import get_session
from app.api.models.user import User


router = APIRouter()


@router.post("/register", response_model=UserModel)
async def create_user(user: UserInputModel, db: AsyncSession = Depends(get_session)):
    db_user = User(username=user.username,
                   full_name=user.full_name,
                   email=user.email,
                   age=user.age,
                   hashed_password=get_password_hash(user.password))
    db.add(db_user)
    try:
        await db.commit()
        return db_user
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email was already registered.")


@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_session)):
    user = await db.execute(select(User).where(User.username == form_data.username))
    user = user.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect.",
                            headers={"WWW-Authenticate": "Bearer"})
    jwt_token = create_access_token({"sub": form_data.username})
    return {"access_token": jwt_token, "token_type": "bearer"}


@router.get("/about_me", response_model=UserModel)
async def read_user(db: AsyncSession = Depends(get_session), username: str = Depends(get_user_by_token)):
    user = await db.execute(select(User).where(User.username == username))
    user = user.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
