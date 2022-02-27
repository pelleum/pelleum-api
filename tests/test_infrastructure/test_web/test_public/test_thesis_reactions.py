import pytest
from httpx import AsyncClient

from app.usecases.schemas.theses import ThesisInDB


@pytest.mark.asyncio
async def test_create_thesis_reaction(
    test_client: AsyncClient, inserted_thesis_object: ThesisInDB
) -> None:

    endpoint = f"/public/theses/reactions/{inserted_thesis_object.thesis_id}"

    response = await test_client.post(endpoint, json={"reaction": 1})

    # Assertions
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_delete_thesis_reaction(
    test_client: AsyncClient, inserted_thesis_object: ThesisInDB
) -> None:

    endpoint = f"/public/theses/reactions/{inserted_thesis_object.thesis_id}"

    # 1. Like a thesis, so the like can be removed
    response = await test_client.post(endpoint, json={"reaction": 1})

    # 2. Remove like on thesis
    response = await test_client.delete(endpoint)

    # Assertions
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_thesis_reaction(
    test_client: AsyncClient, inserted_thesis_object: ThesisInDB
) -> None:

    endpoint = f"/public/theses/reactions/{inserted_thesis_object.thesis_id}"

    # 1. Like a thesis, so the like can be updated
    response = await test_client.post(endpoint, json={"reaction": 1})

    # 2. Updated reaction on thesis
    response = await test_client.patch(endpoint, json={"reaction": -1})

    # Assertions
    assert response.status_code == 200
