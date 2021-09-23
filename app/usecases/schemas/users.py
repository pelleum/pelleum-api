from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str


class UserCreatePasswordHashed(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
    email: Optional[str]
    username: Optional[str]
    password: Optional[str]


class UserUpdatePasswordHashed(BaseModel):
    email: Optional[str]
    username: Optional[str]
    hashed_password: Optional[str]


class UserCreateResponse(UserBase):
    is_active: bool
    is_verified: bool
