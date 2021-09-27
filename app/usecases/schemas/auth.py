from pydantic import BaseModel
from typing import Optional


class JWTResponse(BaseModel):
    access_token: str
    token_type: str


class AuthDataToCreateToken(BaseModel):
    sub: str


class JWTData(BaseModel):
    username: Optional[str] = None
