from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.db.models.user import User


class UserCRUD:
    async def add_user(self, db: AsyncSession, user: UserCreate) -> User:
        db_user = User(
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            age=user.age,
            hashed_password=get_password_hash(user.password),
        )
        db.add(db_user)
        try:
            await db.commit()
            return db_user
        except IntegrityError as e:
            await db.rollback()
            raise e

    async def get_user(self, db: AsyncSession, username: str) -> User:
        user = await db.execute(select(User).where(User.username == username))
        user = user.scalar_one()
        return user


user_crud = UserCRUD()
