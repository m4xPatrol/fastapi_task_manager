from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    age: Annotated[int, Query(gt=18)]


class UserCreate(UserModel):
    password: str
