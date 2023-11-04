from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Cookie,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import UserCreate, UserModel
from app.api.schemas.token import TokenResponse
from app.core.jwt import (
    create_access_token,
    get_user_by_token,
    valid_refresh_token,
    valid_refresh_token_user,
    get_refresh_token_settings,
    create_refresh_token,
    update_refresh_token,
)
from app.core.security import verify_password
from app.db.crud.user import user_crud
from app.db.database import get_session

router = APIRouter()


@router.post("/register", response_model=UserModel)
async def create_user(
    user: UserCreate, db: AsyncSession = Depends(get_session)
) -> UserModel:
    try:
        user_db = await user_crud.add_user(db, user)
        return user_db

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email was already registered.",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_session),
) -> TokenResponse:
    user_db = await user_crud.get_user_by_username(db, form_data.username)

    refresh_token_value = await create_refresh_token(db, user_id=user_db.id)
    response.set_cookie(**get_refresh_token_settings(refresh_token_value))

    if not user_db or not verify_password(form_data.password, user_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password is incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user_db.username})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)


@router.put("/login", response_model=TokenResponse)
async def refresh_tokens(
    response: Response,
    db: AsyncSession = Depends(get_session),
    refresh_token_cookie: str = Cookie(..., alias="refreshToken"),
) -> TokenResponse:
    refresh_token = await valid_refresh_token(db, refresh_token_cookie)
    user = await valid_refresh_token_user(db, refresh_token)

    refresh_token_value = await update_refresh_token(db=db, refresh_token=refresh_token)
    response.set_cookie(**get_refresh_token_settings(refresh_token_value))

    return TokenResponse(
        access_token=create_access_token({"sub": user}),
        refresh_token=refresh_token_value,
    )


@router.get("/about_me", response_model=UserModel)
async def read_user(
    db: AsyncSession = Depends(get_session), username: str = Depends(get_user_by_token)
) -> UserModel:
    user_db = await user_crud.get_user_by_username(db, username)

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user_db
