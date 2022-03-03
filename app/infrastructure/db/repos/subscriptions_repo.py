from typing import Optional

from databases import Database
from sqlalchemy import and_

from app.infrastructure.db.models.public.subscriptions import SUBSCRIPTIONS
from app.usecases.interfaces.subscriptions_repo import ISubscriptionsRepo
from app.usecases.schemas import subscriptions


class SubscriptionsRepo(ISubscriptionsRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, new_subscription: subscriptions.SubscriptionRepoCreate
    ) -> Optional[subscriptions.SubscriptionInDB]:
        """Creates a subscription in the subscriptions table"""

        create_subscriptions_insert_stmt = SUBSCRIPTIONS.insert().values(
            user_id=new_subscription.user_id,
            subscription_tier=new_subscription.subscription_tier,
            stripe_customer_id=new_subscription.stripe_customer_id,
            stripe_subscription_id=new_subscription.stripe_subscription_id,
            is_active=new_subscription.is_active,
        )

        await self.db.execute(create_subscriptions_insert_stmt)

        return await self.retrieve_subscription_with_filter(
            user_id=new_subscription.user_id,
            subscription_tier=new_subscription.subscription_tier,
            stripe_subscription_id=new_subscription.stripe_subscription_id,
        )

    async def update(
        self, updated_subscription: subscriptions.SubscriptionRepoUpdate
    ) -> Optional[subscriptions.SubscriptionInDB]:
        """Updates a subscription in the subscription table"""
        query = SUBSCRIPTIONS.update()

        updated_subscription_dict = {}

        updated_subscription_raw = updated_subscription.dict()
        for key, value in updated_subscription_raw.items():
            if value is not None:
                updated_subscription_dict[key] = value

        query = query.values(updated_subscription_dict)

        if updated_subscription.subscription_id:
            subscription_update_stmt = query.where(
                SUBSCRIPTIONS.c.subscription_id == updated_subscription.subscription_id
            )
        elif updated_subscription.user_id and updated_subscription.subscription_tier:
            conditions = [
                SUBSCRIPTIONS.c.user_id == updated_subscription.user_id,
                SUBSCRIPTIONS.c.subscription_tier
                == updated_subscription.subscription_tier,
            ]
            subscription_update_stmt = query.where(and_(*conditions))
        elif updated_subscription.stripe_subscription_id:
            subscription_update_stmt = query.where(
                SUBSCRIPTIONS.c.stripe_subscription_id
                == updated_subscription.stripe_subscription_id
            )
        else:
            raise Exception(
                "Please pass valid parameter to update by the function, update()"
            )

        await self.db.execute(subscription_update_stmt)

        return await self.retrieve_subscription_with_filter(
            subscription_id=updated_subscription.subscription_id,
            user_id=updated_subscription.user_id,
            subscription_tier=updated_subscription.subscription_tier,
            stripe_subscription_id=updated_subscription.stripe_subscription_id,
        )

    async def retrieve_subscription_with_filter(
        self,
        subscription_id: int = None,
        user_id: int = None,
        subscription_tier: str = None,
        stripe_subscription_id: str = None,
    ) -> Optional[subscriptions.SubscriptionInDB]:
        """Retrieve a subscription given the subscription or (user_id and subscription_tier)"""
        conditions = []

        if subscription_id:
            conditions.append(SUBSCRIPTIONS.c.subscription_id == subscription_id)

        if user_id:
            conditions.append(SUBSCRIPTIONS.c.user_id == user_id)

        if subscription_tier:
            conditions.append(SUBSCRIPTIONS.c.subscription_tier == subscription_tier)

        if stripe_subscription_id:
            conditions.append(
                SUBSCRIPTIONS.c.stripe_subscription_id == stripe_subscription_id
            )

        if not len(conditions):
            raise Exception(
                "Please pass a parameter to query by to the function, retrieve_subscription_with_filter()"
            )

        query = SUBSCRIPTIONS.select().where(and_(*conditions))

        result = await self.db.fetch_one(query)

        return subscriptions.SubscriptionInDB(**result) if result else None
