import pytest
from httpx import AsyncClient

from app.usecases.schemas.posts import PostInDB


@pytest.mark.asyncio
async def test_create_post_reaction(
    test_client: AsyncClient, inserted_post_object: PostInDB
) -> None:

    endpoint = f"/public/posts/reactions/{inserted_post_object.post_id}"

    response = await test_client.post(endpoint, json={"reaction": 1})

    # Assertions
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_delete_post_reaction(
    test_client: AsyncClient, inserted_post_object: PostInDB
) -> None:

    endpoint = f"/public/posts/reactions/{inserted_post_object.post_id}"

    # 1. Like a post, so the like can be removed
    response = await test_client.post(endpoint, json={"reaction": 1})

    # 2. Remove like on post
    response = await test_client.delete(endpoint)

    # Assertions
    assert response.status_code == 200
