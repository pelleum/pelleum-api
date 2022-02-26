from typing import List

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.schemas import posts
from app.usecases.schemas.users import UserInDB

MANY_POSTS_NUMBER_NEEDED = 3


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
async def create_many_posts(
    posts_repo: IPostsRepo, create_post_object: posts.CreatePostRepoAdapter
) -> List[posts.PostInDB]:

    created_posts = []
    for i, _ in enumerate(range(MANY_POSTS_NUMBER_NEEDED)):
        if i % 2 == 0:
            create_post_object.sentiment = posts.Sentiment.BEAR
            create_post_object.asset_symbol = "AAPL"

        created_posts.append(await posts_repo.create(new_post=create_post_object))

    return created_posts


@pytest.mark.asyncio
async def test_create(
    posts_repo: IPostsRepo,
    create_post_object: posts.CreatePostRepoAdapter,
):

    test_post = await posts_repo.create(new_post=create_post_object)

    create_post_object_dict = create_post_object.dict()
    test_post_dict = test_post.dict()

    assert isinstance(test_post, posts.PostInDB)
    for key, value in create_post_object_dict.items():
        assert test_post_dict[key] == value


@pytest.mark.asyncio
async def test_retrieve_many_with_filter(
    posts_repo: IPostsRepo, create_many_posts: List[posts.PostInDB]
):

    test_posts = await posts_repo.retrieve_many_with_filter(
        query_params=posts.PostQueryRepoAdapter(
            user_id=create_many_posts[0].user_id,
            requesting_user_id=create_many_posts[0].user_id,
        )
    )

    assert len(test_posts[0]) >= MANY_POSTS_NUMBER_NEEDED
    for post in test_posts[0]:
        assert isinstance(post, posts.PostInfoFromDB)


@pytest.mark.asyncio
async def test_delete(
    posts_repo: IPostsRepo, inserted_post_object: posts.PostInDB, test_db: Database
):
    # 1. Delete post by post_id
    await posts_repo.delete(post_id=inserted_post_object.post_id)

    # 2. Ensure it no longer exists in the database
    post = await test_db.execute(
        "SELECT * FROM posts WHERE posts.post_id = :post_id",
        {"post_id": inserted_post_object.post_id},
    )

    assert not post
