from abc import ABC, abstractmethod
from typing import List, Optional

from passlib.context import CryptContext

from app.usecases.schemas import users


class IUsersRepo(ABC):
    @abstractmethod
    async def create(
        self, new_user: users.UserCreate, password_context: CryptContext
    ) -> users.UserInDB:
        pass

    @abstractmethod
    async def retrieve_user_with_filter(
        self,
        user_id: str = None,
        email: str = None,
        username: str = None,
    ) -> Optional[users.UserInDB]:
        pass

    @abstractmethod
    async def update(
        self,
        updated_user: users.UserUpdate,
        user_id: str,
        password_context: CryptContext,
    ) -> users.UserInDB:
        pass

    @abstractmethod
    async def manage_blocks(
        self,
        initiating_user_id: str,
        receiving_user_id: str,
        updated_block_list: List[int],
        updated_blocked_by_list: List[int],
    ) -> None:
        """Manage blocked users."""
