from typing import Annotated

from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


int_pk = Annotated[int, mapped_column(primary_key=True)]
