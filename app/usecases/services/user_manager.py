from app.usecases.interfaces.user_manager import IUserManager
from app.usecases.interfaces.user_repo import IUserRepo
from app.usecases.schemas.database import UserInDB
from app.usecases.schemas.auth import AuthDataToCreateToken
from app.usecases.schemas import users
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import JWTError, jwt
from app.settings import settings


class UserManager(IUserManager):
    def __init__(
        self,
        users_repo: IUserRepo,
        password_context: CryptContext,
    ):
        self._users_repo = users_repo
        self.password_context = password_context

    async def create_new_user(self, user: users.UserCreate) -> UserInDB:
        hashed_password = self.password_context.hash(user.password)
        user_raw = user.dict()
        user_raw.update({"hashed_password": hashed_password})

        new_user = users.UserCreatePasswordHashed(**user_raw)

        return await self._users_repo.create(new_user=new_user)

    async def update_user(self, user: users.UserUpdate) -> UserInDB:

        user_raw = user.dict()

        if user.password:
            hashed_password = self.password_context.hash(user.password)
            user_raw.update({"hashed_password": hashed_password})

        updated_user = users.UserUpdatePasswordHashed(**user_raw)

        return self._users_repo.update_user_with_filter(updated_user=updated_user)

    async def authenticate_user(self, user_name: str, password: str) -> UserInDB:

        user: UserInDB = await self._users_repo.retrieve_user_with_filter(username=user_name)

        if not user:
            return False

        if not self.password_context.verify(password, user.hashed_password):
            return False

        return user

    async def create_access_token(self, data: AuthDataToCreateToken) -> str:
        """Creates and returns JSON web token"""
        data_to_encode: dict = data.dict().copy()

        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

        data_to_encode.update({"exp": expire})

        return jwt.encode(
            data_to_encode, settings.json_web_token_secret, algorithm=settings.algorithm
        )
