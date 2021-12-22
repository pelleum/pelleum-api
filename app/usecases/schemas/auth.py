from typing import Optional

from pydantic import BaseModel


class AuthDataToCreateToken(BaseModel):
    sub: str


class JWTData(BaseModel):
    username: Optional[str] = None
