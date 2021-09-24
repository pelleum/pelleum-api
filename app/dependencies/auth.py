from app.usecases.schemas.database import UserInDB
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends
from app.settings import settings
from passlib.context import CryptContext
from app.usecases.schemas import auth
from datetime import datetime, timedelta
from app.libraries.pelleum_errors import inactive_user_error, invalid_credentials
from app.infrastructure.db.repos.user_repo import UsersRepo

from app.dependencies import get_users_repo  # pylint: disable = cyclic-import


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.token_url)


async def get_password_context():
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(user: UserInDB, password: str):
    password_context = await get_password_context()
    return password_context.verify(password, user.hashed_password)


async def create_access_token(data: auth.AuthDataToCreateToken) -> str:
    """Creates and returns JSON web token"""
    data_to_encode: dict = data.dict().copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    data_to_encode.update({"exp": expire})

    return jwt.encode(
        data_to_encode,
        settings.json_web_token_secret,
        algorithm=settings.json_web_token_algorithm,
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates token sent in"""
    try:
        payload = jwt.decode(
            token,
            settings.json_web_token_secret,
            algorithms=[settings.json_web_token_algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise invalid_credentials
        token_data = auth.JWTData(username=username)
    except JWTError:
        raise invalid_credentials  # pylint: disable = raise-missing-from

    return await verify_user_exists(username=token_data.username)


async def verify_user_exists(username: str):
    users_repo: UsersRepo = await get_users_repo()
    user: UserInDB = await users_repo.retrieve_user_with_filter(username=username)
    if user is None:
        raise invalid_credentials
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise inactive_user_error
    return current_user
