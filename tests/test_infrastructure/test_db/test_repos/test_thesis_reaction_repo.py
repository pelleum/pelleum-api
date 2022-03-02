from typing import List, Mapping

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.thesis_reaction_repo import IThesisReactionRepo
from app.usecases.schemas import theses, thesis_reactions
from app.usecases.schemas.users import UserInDB
from tests.conftest import DEFAULT_NUMBER_OF_INSERTED_OBJECTS


@pytest_asyncio.fixture
async def inserted_thesis_reaction(
    thesis_reaction_repo: IThesisReactionRepo,
    inserted_thesis_object: theses.ThesisInDB,
    inserted_user_object: UserInDB,
) -> Mapping[str, int]:

    await thesis_reaction_repo.create(
        thesis_reaction=thesis_reactions.ThesisReactionRepoAdapter(
            thesis_id=inserted_thesis_object.thesis_id,
            user_id=inserted_user_object.user_id,
            reaction=1,
        )
    )

    return {
        "thesis_id": inserted_thesis_object.thesis_id,
        "user_id": inserted_user_object.user_id,
    }


@pytest_asyncio.fixture
async def many_inserted_thesis_reactions(
    thesis_reaction_repo: IThesisReactionRepo,
    many_inserted_theses: List[theses.ThesisInDB],
    inserted_user_object: UserInDB,
) -> Mapping[str, int]:
    """Create many posts, so many post reactions can be created"""

    for thesis in many_inserted_theses:
        await thesis_reaction_repo.create(
            thesis_reaction=thesis_reactions.ThesisReactionRepoAdapter(
                user_id=inserted_user_object.user_id,
                thesis_id=thesis.thesis_id,
                reaction=1,
            )
        )
    return {"user_id": inserted_user_object.user_id}


@pytest.mark.asyncio
async def test_create(
    thesis_reaction_repo: IThesisReactionRepo,
    inserted_thesis_object: theses.ThesisInDB,
    inserted_user_object: UserInDB,
    test_db: Database,
):

    await thesis_reaction_repo.create(
        thesis_reaction=thesis_reactions.ThesisReactionRepoAdapter(
            thesis_id=inserted_thesis_object.thesis_id,
            user_id=inserted_user_object.user_id,
            reaction=1,
        )
    )

    test_reaction = await test_db.fetch_one(
        "SELECT * FROM theses_reactions WHERE thesis_id=:thesis_id AND user_id=:user_id",
        {
            "thesis_id": inserted_thesis_object.thesis_id,
            "user_id": inserted_user_object.user_id,
        },
    )

    assert test_reaction["user_id"] == inserted_user_object.user_id
    assert test_reaction["thesis_id"] == inserted_thesis_object.thesis_id
    assert test_reaction["reaction"] == 1


@pytest.mark.asyncio
async def test_update(
    thesis_reaction_repo: IThesisReactionRepo,
    inserted_thesis_reaction: Mapping[str, int],
    test_db: Database,
):

    # 1. Update the reaction
    await thesis_reaction_repo.update(
        thesis_reaction_update=thesis_reactions.ThesisReactionRepoAdapter(
            user_id=inserted_thesis_reaction["user_id"],
            thesis_id=inserted_thesis_reaction["thesis_id"],
            reaction=-1,
        )
    )
    # 2. Retreive updated reaction
    updated_thesis_reaction = await test_db.fetch_one(
        "SELECT * FROM theses_reactions WHERE theses_reactions.thesis_id = :thesis_id AND theses_reactions.user_id = :user_id",
        {
            "thesis_id": inserted_thesis_reaction["thesis_id"],
            "user_id": inserted_thesis_reaction["user_id"],
        },
    )
    # 3. Verified updated reaction value
    assert updated_thesis_reaction["reaction"] == -1


@pytest.mark.asyncio
async def test_retrieve_many_with_filter(
    thesis_reaction_repo: IThesisReactionRepo,
    many_inserted_thesis_reactions: Mapping[str, int],
):

    test_thesis_reactions = await thesis_reaction_repo.retrieve_many_with_filter(
        query_params=thesis_reactions.ThesisReactionsQueryParams(
            user_id=many_inserted_thesis_reactions["user_id"]
        )
    )

    assert len(test_thesis_reactions[0]) >= DEFAULT_NUMBER_OF_INSERTED_OBJECTS
    for thesis in test_thesis_reactions[0]:
        assert isinstance(thesis, thesis_reactions.ThesisReactionInDB)


@pytest.mark.asyncio
async def test_retrieve_single(
    thesis_reaction_repo: IThesisReactionRepo,
    inserted_thesis_reaction: Mapping[str, int],
):

    test_thesis_reaction = await thesis_reaction_repo.retrieve_single(
        thesis_id=inserted_thesis_reaction["thesis_id"],
        user_id=inserted_thesis_reaction["user_id"],
    )

    assert isinstance(test_thesis_reaction, thesis_reactions.ThesisReactionInDB)
    assert test_thesis_reaction.thesis_id == inserted_thesis_reaction["thesis_id"]
    assert test_thesis_reaction.user_id == inserted_thesis_reaction["user_id"]


@pytest.mark.asyncio
async def test_delete(
    thesis_reaction_repo: IThesisReactionRepo,
    inserted_thesis_reaction: Mapping[str, int],
    test_db: Database,
):

    # 2. Delete thesis by thesis_id
    await thesis_reaction_repo.delete(
        thesis_id=inserted_thesis_reaction["thesis_id"],
        user_id=inserted_thesis_reaction["user_id"],
    )

    # 3. Ensure it no longer exists in the database
    thesis_reaction = await test_db.fetch_one(
        "SELECT * FROM theses_reactions WHERE theses_reactions.thesis_id = :thesis_id AND theses_reactions.user_id = :user_id",
        {
            "thesis_id": inserted_thesis_reaction["thesis_id"],
            "user_id": inserted_thesis_reaction["user_id"],
        },
    )

    assert not thesis_reaction
