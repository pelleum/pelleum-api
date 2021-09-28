from pydantic import BaseModel, constr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: constr(max_length=100) = Field(
        ..., description="The user's email.", example="johndoe@example.com"
    )
    username: constr(max_length=100) = Field(
        ..., description="The user's Pelleum username.", example="johndoe"
    )


class UserCreate(UserBase):
    password: constr(max_length=100) = Field(
        ...,
        description="The user's Pelleum account password.",
        example="Examplepas$word",
    )


class UserUpdate(BaseModel):
    email: Optional[constr(max_length=100)] = Field(
        None, description="The user's email.", example="johndoe@example.com"
    )
    username: Optional[constr(max_length=100)] = Field(
        None, description="The user's Pelleum username.", example="johndoe"
    )
    password: Optional[constr(max_length=100)] = Field(
        None,
        description="The user's Pelleum account password.",
        example="Examplepas$word",
    )


class UserResponse(UserBase):
    user_id: int
    is_active: bool
    is_verified: bool


class UserInDB(UserBase):
    """Database Model"""

    user_id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
