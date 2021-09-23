from pydantic import BaseModel


class JWTResponse(BaseModel):
    access_token: str
    token_type: str


class AuthDataToCreateToken(BaseModel):
    sub: str
