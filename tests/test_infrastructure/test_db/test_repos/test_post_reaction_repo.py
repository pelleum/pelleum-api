from typing import List, Mapping

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.post_reaction_repo import IPostReactionRepo
from app.usecases.schemas import post_reactions, posts
from app.usecases.schemas.users import UserInDB
from tests.conftest import DEFAULT_NUMBER_OF_INSERTED_OBJECTS



@pytest_asyncio.fixture
async def inserted_post_reaction(
    post_reaction_repo: IPostReactionRepo,
    inserted_post_object: posts.PostInDB,
    inserted_user_object: UserInDB,
) -> Mapping[str, int]:

    await post_reaction_repo.create(
        post_reaction=post_reactions.PostReactionRepoAdapter(
            user_id=inserted_user_object.user_id,
            post_id=inserted_post_object.post_id,
            reaction=1,
        )
    )

    return {
        "post_id": inserted_post_object.post_id,
        "user_id": inserted_user_object.user_id,
    }


@pytest_asyncio.fixture
async def many_inserted_post_reactions(
    post_reaction_repo: IPostReactionRepo,
    many_inserted_posts: List[posts.PostInDB],
    inserted_user_object: UserInDB,
) -> Mapping[str, int]:
    """Create many posts, so many post reactions can be created"""

    for post in many_inserted_posts:
        await post_reaction_repo.create(
            post_reaction=post_reactions.PostReactionRepoAdapter(
                user_id=inserted_user_object.user_id,
                post_id=post.post_id,
                reaction=1,
            )
        )
    return {"user_id": inserted_user_object.user_id}


@pytest.mark.asyncio
async def test_create(
    post_reaction_repo: IPostReactionRepo,
    inserted_post_object: posts.PostInDB,
    inserted_user_object: UserInDB,
    test_db: Database,
):

    await post_reaction_repo.create(
        post_reaction=post_reactions.PostReactionRepoAdapter(
            user_id=inserted_user_object.user_id,
            post_id=inserted_post_object.post_id,
            reaction=1,
        )
    )

    test_reaction = await test_db.fetch_one(
        "SELECT * FROM post_reactions WHERE post_id=:post_id AND user_id=:user_id",
        {
            "post_id": inserted_post_object.post_id,
            "user_id": inserted_user_object.user_id,
        },
    )

    assert test_reaction["user_id"] == inserted_user_object.user_id
    assert test_reaction["post_id"] == inserted_post_object.post_id
    assert test_reaction["reaction"] == 1


@pytest.mark.asyncio
async def test_retrieve_many_with_filter(
    post_reaction_repo: IPostReactionRepo,
    many_inserted_post_reactions: Mapping[str, int],
):

    test_post_reactions = await post_reaction_repo.retrieve_many_with_filter(
        query_params=post_reactions.PostsReactionsQueryParams(
            user_id=many_inserted_post_reactions["user_id"]
        )
    )

    assert len(test_post_reactions[0]) >= DEFAULT_NUMBER_OF_INSERTED_OBJECTS
    for post in test_post_reactions[0]:
        assert isinstance(post, post_reactions.PostReactionInDB)


@pytest.mark.asyncio
async def test_delete(
    post_reaction_repo: IPostReactionRepo,
    inserted_post_reaction: Mapping[str, int],
    test_db: Database,
):

    # 1. Delete post by post_id
    await post_reaction_repo.delete(
        post_id=inserted_post_reaction["post_id"],
        user_id=inserted_post_reaction["user_id"],
    )

    # 2. Ensure it no longer exists in the database
    post_reaction = await test_db.fetch_one(
        "SELECT * FROM post_reactions WHERE post_reactions.post_id = :post_id AND post_reactions.user_id = :user_id",
        {
            "post_id": inserted_post_reaction["post_id"],
            "user_id": inserted_post_reaction["user_id"],
        },
    )

    assert not post_reaction
