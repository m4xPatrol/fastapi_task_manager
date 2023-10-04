from typing import Annotated

from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import DeclarativeBase,mapped_column


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


int_pk = Annotated[int, mapped_column(primary_key=True)]
