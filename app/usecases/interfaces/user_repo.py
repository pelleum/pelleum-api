from abc import ABC, abstractmethod
from typing import Union

from passlib.context import CryptContext

from app.usecases.schemas import users
from app.usecases.schemas.users import UserInDB


class IUserRepo(ABC):
    @abstractmethod
    async def create(
        self, new_user: users.UserCreate, password_context: CryptContext
    ) -> UserInDB:
        pass

    @abstractmethod
    async def retrieve_user_with_filter(
        self,
        user_id: str = None,
        email: str = None,
        username: str = None,
    ) -> Union[users.UserInDB, None]:
        pass

    @abstractmethod
    async def update(
        self,
        updated_user: users.UserUpdate,
        user_id: str,
        password_context: CryptContext,
    ) -> UserInDB:
        pass
