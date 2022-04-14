from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas import notifications


class INotificationsRepo(ABC):
    @abstractmethod
    async def create(self, new_event: notifications.NewEventRepoAdapter) -> None:
        """Create reaction."""

    @abstractmethod
    async def update(self, notification_id: int) -> None:
        """Update notification acknowledgement."""

    @abstractmethod
    async def retrieve_many(
        self,
        user_id: int,
        page_number: int = 1,
        page_size: int = 200,
    ) -> List[notifications.NotificationDbInfo]:
        """Retrieve many reactions"""

    @abstractmethod
    async def retrieve_single(
        self,
        notification_id: int,
    ) -> Optional[notifications.NotificationDbInfo]:
        """Retrieves a single notification."""
