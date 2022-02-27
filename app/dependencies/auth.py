import re
from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.dependencies import get_users_repo  # pylint: disable = cyclic-import
from app.libraries import pelleum_errors
from app.settings import settings
from app.usecases.schemas import auth
from app.usecases.schemas.users import UserInDB

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


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Validates token sent in"""
    try:
        payload = jwt.decode(
            token,
            settings.json_web_token_secret,
            algorithms=[settings.json_web_token_algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise await pelleum_errors.PelleumErrors().invalid_credentials()
        token_data = auth.JWTData(username=username)
    except JWTError:
        raise await pelleum_errors.PelleumErrors().invalid_credentials()  # pylint: disable = raise-missing-from

    return await verify_user_exists(username=token_data.username)


async def verify_user_exists(username: str) -> UserInDB:
    users_repo = await get_users_repo()
    user = await users_repo.retrieve_user_with_filter(username=username)
    if user is None:
        raise await pelleum_errors.PelleumErrors().invalid_credentials()
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    if not current_user.is_active:
        raise await pelleum_errors.PelleumErrors().inactive_user()
    return current_user


async def validate_password(password: str) -> None:
    """This function checks the validity of the password sent in upon user creation"""

    # fmt: off
    special_symbols = special_symbols = (
        "!", "#", "$",",", "%", "&", "'", "(", ")", "*", "+",
        "-", ".", "/", ":", ";", "<", "=", ">", "?", "@",
        "[", "]", "^", "_", "`", "{", "|", "}", "~"
    )
    # fmt: on

    if len(password) < 8:
        raise await pelleum_errors.PelleumErrors(
            detail="Password must be at least 8 characters long."
        ).invalid_password()

    if not any(char.isdigit() for char in password):
        raise await pelleum_errors.PelleumErrors(
            detail="Password must contain at least 1 digit."
        ).invalid_password()

    if not any(char.isupper() for char in password):
        raise await pelleum_errors.PelleumErrors(
            detail="Password must contain at least one uppercase letter."
        ).invalid_password()

    if not any(char.islower() for char in password):
        raise await pelleum_errors.PelleumErrors(
            detail="Password must contain at least one lowercase letter."
        ).invalid_password()

    if not any(char in special_symbols for char in password):
        raise await pelleum_errors.PelleumErrors(
            detail="Password must contain at least one special character."
        ).invalid_password()


async def validate_email(email: str) -> None:
    """This function checks the validity of the email sent in upon user creation"""

    # Regular expression for validating an email (look into what this is doing)
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    if not re.fullmatch(regex, email):
        raise await pelleum_errors.PelleumErrors(
            detail="Email format is invalid. Please submit a valid email."
        ).invalid_email()
