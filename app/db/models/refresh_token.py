from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


uuid_pk = Annotated[UUID, mapped_column(primary_key=True)]
timestamp = Annotated[datetime, mapped_column(nullable=False)]


class RefreshToken(Base):
    uuid: Mapped[uuid_pk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[timestamp]
    created_at: Mapped[timestamp] = mapped_column(server_default=func.now())
    updated_at: Mapped[timestamp] = mapped_column(onupdate=func.now(), nullable=True)
