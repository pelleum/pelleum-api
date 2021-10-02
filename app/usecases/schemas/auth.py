from typing import Optional

from pydantic import BaseModel


class JWTResponse(BaseModel):
    access_token: str
    token_type: str


class AuthDataToCreateToken(BaseModel):
    sub: str


class JWTData(BaseModel):
    username: Optional[str] = None
