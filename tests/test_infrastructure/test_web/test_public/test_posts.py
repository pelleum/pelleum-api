from typing import List, Mapping

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.usecases.schemas.posts import PostInDB, PostResponse


@pytest_asyncio.fixture
async def create_post_request_json() -> Mapping[str, str]:
    return {
        "content": "This is a test post.",
        "asset_symbol": "AAPL",
        "sentiment": "Bear",
    }


@pytest.mark.asyncio
async def test_create_new_post(
    test_client: AsyncClient, create_post_request_json: Mapping[str, str]
) -> None:

    endpoint = "/public/posts"

    response = await test_client.post(endpoint, json=create_post_request_json)
    response_data = response.json()
    expected_response_fields = [field for field in PostResponse.__fields__]

    # Assertions
    assert response.status_code == 201
    for key, value in response_data.items():
        assert key in expected_response_fields
        if key in create_post_request_json:
            assert value == create_post_request_json.get(key)


@pytest.mark.asyncio
async def test_get_post(
    test_client: AsyncClient, inserted_post_object: PostInDB
) -> None:

    endpoint = f"/public/posts/{inserted_post_object.post_id}"

    # Test successful user creation
    response = await test_client.get(endpoint)
    response_data = response.json()
    expected_response_fields = [field for field in PostResponse.__fields__]

    # Assertions
    assert response.status_code == 200
    for key, value in response_data.items():
        assert key in expected_response_fields
        if key != "created_at" and key != "updated_at":
            assert value == inserted_post_object.dict().get(key)


@pytest.mark.asyncio
async def test_get_many_posts(
    test_client: AsyncClient, many_inserted_posts: List[PostInDB]
) -> None:

    endpoint = "/public/posts/retrieve/many"
    params = {"user_id": many_inserted_posts[0].user_id}

    response = await test_client.get(endpoint, params=params)
    response_data = response.json().get("records").get("posts")
    expected_response_fields = [field for field in PostResponse.__fields__]

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(many_inserted_posts)
    for key in response_data[0]:
        assert key in expected_response_fields


@pytest.mark.asyncio
async def test_delete_post(
    test_client: AsyncClient, inserted_post_object: PostInDB
) -> None:

    endpoint = f"/public/posts/{inserted_post_object.post_id}"

    response = await test_client.delete(endpoint)

    # Assertions
    assert response.status_code == 200
