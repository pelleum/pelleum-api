from typing import Mapping

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.usecases.schemas.subscriptions import StripeSubscription, SubscriptionInDB


@pytest_asyncio.fixture
async def create_subscription_request_json() -> Mapping[str, str]:
    return {"subscription_tier": "PRO", "price_id": "pri_123"}


@pytest.mark.asyncio
async def test_create_subscription(
    test_client: AsyncClient,
    create_subscription_request_json: Mapping[str, str],
):
    endpoint = "/public/subscriptions/create"
    response = await test_client.post(endpoint, json=create_subscription_request_json)
    response_data = response.json()
    expected_response_fields = [field for field in StripeSubscription.__fields__]
    assert response.status_code == 201
    for key in response_data.keys():
        assert key in expected_response_fields
    assert response_data["id"] == "sub_123"
    assert response_data["client_secret"] == "src_123"


@pytest.mark.asyncio
async def test_cancel_subscription(test_client: AsyncClient):
    test_json = {"stripe_subscription_id": "sub_123"}
    endpoint = "public/subscriptions/cancel"
    response = await test_client.post(endpoint, json=test_json)
    response_data = response.json()
    expected_response_fields = [field for field in StripeSubscription.__fields__]
    assert response.status_code == 201
    for key in response_data.keys():
        assert key in expected_response_fields
    assert response_data["id"] == test_json["stripe_subscription_id"]


@pytest.mark.asyncio
async def test_get_subscription(
    test_client: AsyncClient,
    inserted_subscription_object: SubscriptionInDB,
):
    test_subscription_tier = inserted_subscription_object.subscription_tier
    endpoint = f"public/subscriptions/{test_subscription_tier}"
    response = await test_client.get(endpoint)
    response_data = response.json()
    expected_response_fields = [field for field in SubscriptionInDB.__fields__]
    assert response.status_code == 200
    for key in response_data.keys():
        assert key in expected_response_fields
    assert response_data["user_id"] == inserted_subscription_object.user_id
    assert (
        response_data["subscription_id"] == inserted_subscription_object.subscription_id
    )
    assert (
        response_data["stripe_subscription_id"]
        == inserted_subscription_object.stripe_subscription_id
    )


@pytest.mark.asyncio
async def test_webhook_received(test_client: AsyncClient):
    endpoint = "public/subscriptions/webhook_received"
    response = await test_client.post(endpoint, json={})
    assert response.status_code == 200
