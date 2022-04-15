from typing import List, Mapping

import pytest
import pytest_asyncio
from databases import Database
from httpx import AsyncClient

from app.usecases.schemas.theses import ThesisInDB, ThesisResponse


@pytest_asyncio.fixture
async def create_thesis_request_json() -> Mapping[str, str]:
    return {
        "title": "Thesis on a Test Asset!",
        "content": "This is a test thesis!",
        "asset_symbol": "BTC",
        "sentiment": "Bull",
        "sources": ["https://www.pelleum.com", "https://www.youtube.com"],
    }


@pytest_asyncio.fixture
async def update_thesis_request_json() -> Mapping[str, str]:
    return {
        "title": "Thsis Updated!",
        "content": "This is an updated thesis!",
        "asset_symbol": "BTC",
        "sentiment": "Bear",
        "sources": ["https://www.bitcoin.org", "https://www.youtube.com"],
    }


@pytest.mark.asyncio
async def test_create_new_thesis(
    test_client: AsyncClient, create_thesis_request_json: Mapping[str, str]
) -> None:

    endpoint = "/public/theses"

    response = await test_client.post(endpoint, json=create_thesis_request_json)
    response_data = response.json()
    expected_response_fields = [field for field in ThesisResponse.__fields__]

    # Assertions
    assert response.status_code == 201
    for key, value in response_data.items():
        assert key in expected_response_fields
        if key in create_thesis_request_json:
            assert value == create_thesis_request_json.get(key)


@pytest.mark.asyncio
async def test_get_thesis(
    test_client: AsyncClient, inserted_thesis_object: ThesisInDB
) -> None:

    endpoint = f"/public/theses/{inserted_thesis_object.thesis_id}"

    # Test successful user creation
    response = await test_client.get(endpoint)
    response_data = response.json()
    expected_response_fields = [field for field in ThesisResponse.__fields__]

    # Assertions
    non_inserted_thesis_object_keys = {
        "created_at",
        "updated_at",
        "like_count",
        "dislike_count",
        "save_count",
    }
    assert response.status_code == 200
    for key, value in response_data.items():
        assert key in expected_response_fields
        if key not in non_inserted_thesis_object_keys:
            assert value == inserted_thesis_object.dict().get(key)


@pytest.mark.asyncio
async def test_get_many_theses(
    test_client: AsyncClient, many_inserted_theses: List[ThesisInDB]
) -> None:

    endpoint = "/public/theses/retrieve/many"
    params = {"user_id": many_inserted_theses[0].user_id}

    response = await test_client.get(endpoint, params=params)
    response_data = response.json().get("records").get("theses")
    expected_response_fields = [field for field in ThesisResponse.__fields__]

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(many_inserted_theses)
    for key in response_data[0]:
        assert key in expected_response_fields


@pytest.mark.asyncio
async def test_update_thesis(
    test_client: AsyncClient,
    inserted_thesis_object: ThesisInDB,
    update_thesis_request_json: Mapping[str, str],
) -> None:

    endpoint = f"/public/theses/{inserted_thesis_object.thesis_id}"

    response = await test_client.patch(endpoint, json=update_thesis_request_json)
    response_data = response.json()
    expected_response_fields = [field for field in ThesisResponse.__fields__]

    # Assertions
    assert response.status_code == 200
    for key, value in response_data.items():
        assert key in expected_response_fields
        if key in update_thesis_request_json:
            assert value == update_thesis_request_json.get(key)


@pytest.mark.asyncio
async def test_delete_thesis(
    test_client: AsyncClient,
    inserted_thesis_object: ThesisInDB,
    update_thesis_request_json: Mapping[str, str],
    test_db: Database,
) -> None:

    endpoint = f"/public/theses/{inserted_thesis_object.thesis_id}"

    response = await test_client.delete(endpoint)

    test_thesis = await test_db.fetch_one(
        "SELECT * FROM theses WHERE thesis_id=:thesis_id",
        {
            "thesis_id": inserted_thesis_object.thesis_id,
        },
    )

    # Assertions
    assert response.status_code == 200
    assert not test_thesis
