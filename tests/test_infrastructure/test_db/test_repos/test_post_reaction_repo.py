from typing import List, Mapping

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.post_reaction_repo import IPostReactionRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.schemas import post_reactions, posts
from app.usecases.schemas.users import UserInDB

MANY_REACTIONS_NUMBER_NEEDED = 3


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
async def create_post_object(
    inserted_user_object: UserInDB,
) -> posts.CreatePostRepoAdapter:
    return posts.CreatePostRepoAdapter(
        content="This is a test post!",
        asset_symbol="TSLA",
        sentiment=posts.Sentiment.BULL,
        user_id=inserted_user_object.user_id,
        username=inserted_user_object.username,
    )


@pytest_asyncio.fixture
async def many_inserted_posts(
    posts_repo: IPostsRepo,
    create_post_object: posts.CreatePostRepoAdapter,
) -> List[posts.PostInDB]:
    """Create many posts, so many post reactions can be created"""

    return [
        await posts_repo.create(new_post=create_post_object)
        for _ in range(MANY_REACTIONS_NUMBER_NEEDED)
    ]


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

    assert len(test_post_reactions[0]) >= MANY_REACTIONS_NUMBER_NEEDED
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
