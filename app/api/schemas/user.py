from pydantic import BaseModel, EmailStr
from fastapi import Query
from typing import Annotated


class UserModel(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    age: Annotated[int, Query(gt=18)]


class UserInputModel(UserModel):
    password: str
