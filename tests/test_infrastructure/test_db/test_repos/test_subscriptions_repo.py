import pytest
import pytest_asyncio

from app.usecases.interfaces.subscriptions_repo import ISubscriptionsRepo
from app.usecases.schemas.subscriptions import (
    SubscriptionInDB,
    SubscriptionRepoCreate,
    SubscriptionRepoUpdate,
)
from app.usecases.schemas.users import UserInDB


@pytest_asyncio.fixture
def create_subscription_object(
    inserted_user_object: UserInDB,
) -> SubscriptionRepoCreate:
    return SubscriptionRepoCreate(
        user_id=inserted_user_object.user_id,
        subscription_tier="PRO",
        stripe_customer_id="cus_123test",
        stripe_subscription_id="sub_123test",
        is_active=False,
    )


@pytest.mark.asyncio
async def test_create(
    subscriptions_repo: ISubscriptionsRepo,
    create_subscription_object: SubscriptionRepoCreate,
):

    test_subscription = await subscriptions_repo.create(
        new_subscription=create_subscription_object
    )

    assert isinstance(test_subscription, SubscriptionInDB)
    assert test_subscription.user_id == create_subscription_object.user_id
    assert (
        test_subscription.subscription_tier
        == create_subscription_object.subscription_tier
    )
    assert (
        test_subscription.stripe_customer_id
        == create_subscription_object.stripe_customer_id
    )
    assert (
        test_subscription.stripe_subscription_id
        == create_subscription_object.stripe_subscription_id
    )
    assert test_subscription.is_active == create_subscription_object.is_active


@pytest.mark.asyncio
async def test_update(
    subscriptions_repo: ISubscriptionsRepo,
    inserted_subscription_object: SubscriptionInDB,
):

    updated_record = SubscriptionRepoUpdate(
        stripe_subscription_id=inserted_subscription_object.stripe_subscription_id,
        is_active=True,
    )
    test_subscription = await subscriptions_repo.update(
        updated_subscription=updated_record
    )

    assert isinstance(test_subscription, SubscriptionInDB)
    assert (
        test_subscription.stripe_subscription_id
        == inserted_subscription_object.stripe_subscription_id
    )
    assert test_subscription.is_active == True
    assert (
        test_subscription.subscription_id
        == inserted_subscription_object.subscription_id
    )


@pytest.mark.asyncio
async def test_retrieve_subscription_with_filter(
    subscriptions_repo: ISubscriptionsRepo,
    inserted_subscription_object: SubscriptionInDB,
):

    test_subscription = await subscriptions_repo.retrieve_subscription_with_filter(
        subscription_id=inserted_subscription_object.subscription_id
    )

    assert isinstance(test_subscription, SubscriptionInDB)
    assert (
        test_subscription.subscription_id
        == inserted_subscription_object.subscription_id
    )
    assert test_subscription.is_active == inserted_subscription_object.is_active
    assert (
        test_subscription.stripe_customer_id
        == inserted_subscription_object.stripe_customer_id
    )
