from typing import List

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.rationales_repo import IRationalesRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.schemas import rationales, theses
from app.usecases.schemas.users import UserInDB
from tests.conftest import DEFAULT_NUMBER_OF_INSERTED_OBJECTS

DEFAULT_NUMBER_OF_INSERTED_OBJECTS = 3


@pytest_asyncio.fixture
async def create_many_rationales(
    rationales_repo: IRationalesRepo, many_inserted_theses: List[theses.ThesisInDB]
) -> List[rationales.RationaleWithThesis]:

    created_rationales = []
    for created_thesis in many_inserted_theses:
        created_rationales.append(
            await rationales_repo.create(
                thesis_id=created_thesis.thesis_id, user_id=created_thesis.user_id
            )
        )

    return created_rationales


@pytest_asyncio.fixture
async def inserted_rationale_object(
    rationales_repo: IRationalesRepo, inserted_thesis_object: theses.ThesisInDB
) -> rationales.RationaleWithThesis:
    """Inserted rationale for tests to use."""

    return await rationales_repo.create(
        thesis_id=inserted_thesis_object.thesis_id,
        user_id=inserted_thesis_object.user_id,
    )


@pytest.mark.asyncio
async def test_create(
    rationales_repo: IRationalesRepo,
    inserted_thesis_object: theses.ThesisInDB,
    inserted_user_object: UserInDB,
):
    """Tests creation of a rationale that another user wrote."""

    test_rationale = await rationales_repo.create(
        thesis_id=inserted_thesis_object.thesis_id, user_id=inserted_user_object.user_id
    )

    test_rationale_dict = test_rationale.dict()
    inserted_thesis_dict = inserted_thesis_object.dict()

    assert isinstance(test_rationale, rationales.RationaleWithThesis)
    assert test_rationale.thesis_id == inserted_thesis_object.thesis_id
    assert test_rationale.user_id == inserted_user_object.user_id
    for key, value in test_rationale_dict.items():
        if key[0:7] == "thesis_" and value is not None:
            if key == "thesis_id":
                assert inserted_thesis_dict[key] == value
            else:
                assert inserted_thesis_dict[key[7:]] == value


@pytest.mark.asyncio
async def test_retrieve_many_rationales_with_filter(
    rationales_repo: IRationalesRepo,
    create_many_rationales: List[rationales.RationaleWithThesis],
):

    test_rationales = await rationales_repo.retrieve_many_rationales_with_filter(
        query_params=rationales.RationaleQueryRepoAdapter(
            user_id=create_many_rationales[0].user_id
        )
    )

    assert len(test_rationales[0]) >= DEFAULT_NUMBER_OF_INSERTED_OBJECTS
    for rationale in test_rationales[0]:
        assert isinstance(rationale, rationales.RationaleWithThesis)


@pytest.mark.asyncio
async def test_delete(
    rationales_repo: IRationalesRepo,
    inserted_rationale_object: rationales.RationaleWithThesis,
    test_db: Database,
):
    # 1. Delete rationale by rationale_id
    await rationales_repo.delete(rationale_id=inserted_rationale_object.rationale_id)

    # 2. Ensure it no longer exists in the database
    rationale = await test_db.fetch_one(
        "SELECT * FROM rationales WHERE rationales.rationale_id = :rationale_id",
        {"rationale_id": inserted_rationale_object.rationale_id},
    )

    assert not rationale
