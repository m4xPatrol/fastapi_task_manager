from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, int_pk

user_fk = Annotated[int, mapped_column(ForeignKey("user.id"))]


class Task(Base):
    id: Mapped[int_pk]
    title: Mapped[str]
    description: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)
    owner_id: Mapped[user_fk]
    owner: Mapped["User"] = relationship(back_populates="tasks")
