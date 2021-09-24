from abc import ABC, abstractmethod
from app.usecases.schemas import users
from app.usecases.schemas.database import UserInDB
from passlib.context import CryptContext


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
    ) -> UserInDB:
        pass

    @abstractmethod
    async def update(
        self,
        updated_user: users.UserUpdate,
        user_id: str,
        password_context: CryptContext,
    ) -> UserInDB:
        pass
