from typing import List

import pytest
import pytest_asyncio

from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.schemas import theses
from app.usecases.schemas.users import UserInDB

MANY_THESES_NUMBER_NEEDED = 3


@pytest_asyncio.fixture
async def create_thesis_object(
    inserted_user_object: UserInDB,
) -> theses.CreateThesisRepoAdapter:
    return theses.CreateThesisRepoAdapter(
        title="Test Thesis Title",
        content="This is a test thesis on a test asset.",
        asset_symbol="BTC",
        sentiment=theses.Sentiment.BULL,
        sources=["https://www.pelleum.com", "https://www.youtube.com"],
        user_id=inserted_user_object.user_id,
        username=inserted_user_object.username,
    )


@pytest_asyncio.fixture
async def update_thesis_object(
    inserted_thesis_object: theses.ThesisInDB,
) -> theses.UpdateThesisRepoAdapter:
    return theses.UpdateThesisRepoAdapter(
        title="Updated Thesis Title",
        content="Updated thesis content",
        thesis_id=inserted_thesis_object.thesis_id,
    )


@pytest_asyncio.fixture
async def create_many_theses(
    theses_repo: IThesesRepo, create_thesis_object: theses.CreateThesisRepoAdapter
) -> List[theses.ThesisInDB]:

    created_theses = []
    for i, _ in enumerate(range(MANY_THESES_NUMBER_NEEDED)):
        create_thesis_object.title += str(i)

        created_theses.append(await theses_repo.create(thesis=create_thesis_object))

    return created_theses


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
    theses_repo: IThesesRepo, create_many_theses: List[theses.ThesisInDB]
):

    test_theses = await theses_repo.retrieve_many_with_filter(
        query_params=theses.ThesesQueryRepoAdapter(
            user_id=create_many_theses[0].user_id,
            requesting_user_id=create_many_theses[0].user_id,
        )
    )

    assert len(test_theses[0]) >= MANY_THESES_NUMBER_NEEDED
    for thesis in test_theses[0]:
        assert isinstance(thesis, theses.ThesisWithUserReaction)
