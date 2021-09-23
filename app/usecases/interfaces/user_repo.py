from abc import ABC, abstractmethod
from app.usecases.schemas import users
from app.usecases.schemas.database import UserInDB


class IUserRepo(ABC):
    @abstractmethod
    async def create(self, new_user: users.UserCreatePasswordHashed) -> UserInDB:
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
    async def update_user_with_filter(
        self, updated_user: users.UserUpdatePasswordHashed, user_id: str
    ) -> UserInDB:
        pass
