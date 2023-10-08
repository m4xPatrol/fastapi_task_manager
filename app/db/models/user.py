from typing import Annotated

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, int_pk

unique_str_k = Annotated[str, mapped_column(unique=True, nullable=False)]


class User(Base):
    id: Mapped[int_pk]
    username: Mapped[unique_str_k]
    full_name: Mapped[str]
    email: Mapped[unique_str_k]
    age: Mapped[int]
    hashed_password: Mapped[bytes]
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")
