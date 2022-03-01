# import pytest
# import pytest_asyncio

# from app.usecases.interfaces.subscriptions_repo import ISubscriptionsRepo
# from app.usecases.schemas.subscriptions import SubscriptionInDB


# @pytest_asyncio.fixture
# def create_subscription_object() -> SubscriptionInDB:
#     return SubscriptionInDB(
#         user_id=1,
#         subscription_tier="PRO",
#         stripe_customer_id="cus_123test",
#         stripe_subscription_id="sub_123test",
#         is_active=False
#     )

# @pytest.mark.asyncio
# async def test_create(
#     subscriptions_repo: ISubscriptionsRepo,
#     user_id: int,
#     subscription_tier: str,
#     stripe_customer_id: str,
#     stripe_subscription_id: str,
#     is_active: bool
# ):

#     test_subscription = await subscriptions_repo.create(
#         user_id=user_id,
#         subscription_tier=subscription_tier,
#         stripe_customer_id=stripe_customer_id,
#         stripe_subscription_id=stripe_subscription_id,
#         is_active=is_active
#     )

#     assert isinstance(test_subscription, SubscriptionInDB)
#     assert test_subscription.user_id == create_subscription_object.user_id
