from abc import ABC, abstractmethod
from typing import Optional

from app.usecases.schemas import subscriptions


class ISubscriptionsRepo(ABC):
    @abstractmethod
    async def create(
        self, new_subscription: subscriptions.SubscriptionRepoCreate
    ) -> Optional[subscriptions.SubscriptionInDB]:
        """Creates a subscription in the subscriptions table"""

    @abstractmethod
    async def update(
        self, updated_subscription: subscriptions.SubscriptionRepoUpdate
    ) -> Optional[subscriptions.SubscriptionInDB]:
        """Updates a subscription in the subscription table"""

    @abstractmethod
    async def retrieve_subscription_with_filter(
        self,
        subscription_id: int = None,
        user_id: int = None,
        subscription_tier: str = None,
        stripe_subscription_id: str = None,
    ) -> Optional[subscriptions.SubscriptionInDB]:
        """Retrieve a subscription given the subscription or (user_id and subscription_tier)"""
