from abc import ABC, abstractmethod


class IUserManager(ABC):
    @abstractmethod
    async def authenticate_user(self, user_name: str, password: str):
        pass
