from typing import List

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.usecases.interfaces.rationales_repo import IRationalesRepo
from app.usecases.schemas.rationales import RationaleResponse, RationaleWithThesis
from app.usecases.schemas.theses import ThesisInDB
from app.usecases.schemas.users import UserInDB


@pytest_asyncio.fixture
async def insert_many_rationales(
    rationales_repo: IRationalesRepo,
    many_inserted_theses: List[ThesisInDB],
    inserted_user_object: UserInDB,
) -> List[RationaleWithThesis]:

    return [
        await rationales_repo.create(
            thesis_id=thesis.thesis_id, user_id=inserted_user_object.user_id
        )
        for thesis in many_inserted_theses
    ]


@pytest_asyncio.fixture
async def inserted_rationale_object(
    rationales_repo: IRationalesRepo, inserted_thesis_object: ThesisInDB
) -> RationaleWithThesis:
    """Inserted rationale for tests to use."""

    return await rationales_repo.create(
        thesis_id=inserted_thesis_object.thesis_id,
        user_id=inserted_thesis_object.user_id,
    )


@pytest.mark.asyncio
async def test_add_thesis_to_rationales(
    test_client: AsyncClient, inserted_thesis_object: ThesisInDB
) -> None:

    endpoint = "/public/theses/rationales"

    response = await test_client.post(
        endpoint, json={"thesis_id": inserted_thesis_object.thesis_id}
    )
    response_data = response.json()
    expected_rationale_response_fields = [
        field for field in RationaleResponse.__fields__
    ]
    expected_thesis_response_fields = [field for field in ThesisInDB.__fields__]

    # Assertions
    assert response.status_code == 201
    for key, value in response_data.items():
        assert key in expected_rationale_response_fields
        if key == "thesis_id":
            assert value == inserted_thesis_object.thesis_id
        if key == "thesis":
            for sub_key, sub_value in value.items():
                assert sub_key in expected_thesis_response_fields
                if sub_key != "created_at" and sub_key != "updated_at":
                    assert sub_value == inserted_thesis_object.dict().get(sub_key)


@pytest.mark.asyncio
async def test_get_many_rationales(
    test_client: AsyncClient, insert_many_rationales: List[RationaleWithThesis]
) -> None:

    endpoint = f"/public/theses/rationales/retrieve/many"
    params = {"user_id": insert_many_rationales[0].user_id}

    # Test successful user creation
    response = await test_client.get(endpoint, params=params)
    response_data = response.json().get("records").get("rationales")
    expected_rationale_response_fields = [
        field for field in RationaleResponse.__fields__
    ]
    expected_thesis_response_fields = [field for field in ThesisInDB.__fields__]

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(insert_many_rationales)
    for rationale in response_data:
        for key, value in rationale.items():
            assert key in expected_rationale_response_fields
            if key == "thesis":
                for sub_key in value:
                    assert sub_key in expected_thesis_response_fields


@pytest.mark.asyncio
async def test_delete_rationale(
    test_client: AsyncClient, inserted_rationale_object: RationaleWithThesis
) -> None:

    endpoint = f"/public/theses/rationales/{inserted_rationale_object.rationale_id}"

    response = await test_client.delete(endpoint)

    # Assertions
    assert response.status_code == 200
