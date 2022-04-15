from typing import List

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.schemas import theses
from app.usecases.schemas.users import UserInDB
from tests.conftest import DEFAULT_NUMBER_OF_INSERTED_OBJECTS


@pytest_asyncio.fixture
async def update_thesis_object(
    inserted_thesis_object: theses.ThesisInDB,
) -> theses.UpdateThesisRepoAdapter:
    return theses.UpdateThesisRepoAdapter(
        title="Updated Thesis Title",
        content="Updated thesis content",
        thesis_id=inserted_thesis_object.thesis_id,
    )


@pytest.mark.asyncio
async def test_create(
    theses_repo: IThesesRepo,
    create_thesis_object: theses.CreateThesisRepoAdapter,
):

    test_thesis = await theses_repo.create(thesis=create_thesis_object)

    create_thesis_object_dict = create_thesis_object.dict()
    test_post_dict = test_thesis.dict()

    assert isinstance(test_thesis, theses.ThesisInDB)
    for key, value in create_thesis_object_dict.items():
        assert test_post_dict[key] == value


@pytest.mark.asyncio
async def test_update(
    theses_repo: IThesesRepo, update_thesis_object: theses.UpdateThesisRepoAdapter
):

    test_updated_thesis = await theses_repo.update(updated_thesis=update_thesis_object)

    assert isinstance(test_updated_thesis, theses.ThesisInDB)
    assert test_updated_thesis.title == update_thesis_object.title
    assert test_updated_thesis.content == update_thesis_object.content


@pytest.mark.asyncio
async def test_retrieve_many_with_filter(
    theses_repo: IThesesRepo, many_inserted_theses: List[theses.ThesisInDB]
):

    test_theses = await theses_repo.retrieve_many_with_filter(
        user_id=many_inserted_theses[0].user_id,
        query_params=theses.ThesesQueryRepoAdapter(
            user_id=many_inserted_theses[0].user_id,
            requesting_user_id=many_inserted_theses[0].user_id,
        ),
    )

    assert len(test_theses[0]) >= DEFAULT_NUMBER_OF_INSERTED_OBJECTS
    for thesis in test_theses[0]:
        assert isinstance(thesis, theses.ThesisWithInteractionData)


@pytest.mark.asyncio
async def test_retrieve_thesis_with_reaction(
    theses_repo: IThesesRepo,
    inserted_thesis_object: theses.ThesisInDB,
    inserted_user_object: UserInDB,
):

    test_thesis = await theses_repo.retrieve_thesis_with_reaction(
        thesis_id=inserted_thesis_object.thesis_id, user_id=inserted_user_object.user_id
    )

    assert isinstance(test_thesis, theses.ThesisWithInteractionData)
    assert test_thesis.title == inserted_thesis_object.title
    assert test_thesis.content == inserted_thesis_object.content


@pytest.mark.asyncio
async def test_delete(
    theses_repo: IThesesRepo,
    inserted_thesis_object: theses.ThesisInDB,
    test_db: Database,
):
    # 1. Delete thesis by thesis_id
    await theses_repo.delete(thesis_id=inserted_thesis_object.thesis_id)

    # 2. Ensure it no longer exists in the database
    thesis = await test_db.fetch_one(
        "SELECT * FROM theses WHERE theses.thesis_id = :thesis_id",
        {"thesis_id": inserted_thesis_object.thesis_id},
    )

    assert not thesis
