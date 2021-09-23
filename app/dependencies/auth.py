from fastapi.security import OAuth2PasswordBearer
from app.settings import settings


async def get_oauth2_scheme():
    return OAuth2PasswordBearer(tokenUrl=settings.token_url)