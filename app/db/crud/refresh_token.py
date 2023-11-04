from pydantic import UUID4
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.refresh_token import RefreshToken
from app.core.config import settings


class RefreshTokenCRUD:
    async def create_refresh_token(
        self, db: AsyncSession, user_id: int, expires_at: datetime, refresh_token: str
    ) -> str:
        insert_query = RefreshToken(
            uuid=uuid.uuid4(),
            refresh_token=refresh_token,
            expires_at=expires_at,
            user_id=user_id,
        )
        db.add(insert_query)

        try:
            await db.commit()
            return refresh_token
        except IntegrityError as e:
            await db.rollback()
            raise e

    async def get_refresh_token(
        self, db: AsyncSession, refresh_token: str
    ) -> RefreshToken | None:
        select_query = await db.execute(
            select(RefreshToken).where(RefreshToken.refresh_token == refresh_token)
        )
        return select_query.scalar_one_or_none()

    async def expire_refresh_token(
        self, db: AsyncSession, refresh_token_uuid: UUID4
    ) -> None:
        await db.execute(
            update(RefreshToken)
            .values(expires_at=datetime.utcnow() - timedelta(days=1))
            .where(RefreshToken.uuid == refresh_token_uuid)
        )
        await db.commit()

    async def update_refresh_token(
        self,
        db: AsyncSession,
        refresh_token: RefreshToken,
        new_refresh_token_value: str,
    ) -> None:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.uuid == refresh_token.uuid)
            .values(
                expires_at=datetime.utcnow()
                + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
                refresh_token=new_refresh_token_value,
            )
        )
        await db.commit()


refresh_token_crud = RefreshTokenCRUD()
