from typing import List

import pytest
from databases import Database

from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.schemas import posts
from tests.conftest import DEFAULT_NUMBER_OF_INSERTED_OBJECTS


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
    posts_repo: IPostsRepo, many_inserted_posts: List[posts.PostInDB]
):

    test_posts = await posts_repo.retrieve_many_with_filter(
        query_params=posts.PostQueryRepoAdapter(
            user_id=many_inserted_posts[0].user_id,
            requesting_user_id=many_inserted_posts[0].user_id,
        )
    )

    assert len(test_posts[0]) >= DEFAULT_NUMBER_OF_INSERTED_OBJECTS
    for post in test_posts[0]:
        assert isinstance(post, posts.PostInfoFromDB)


@pytest.mark.asyncio
async def test_delete(
    posts_repo: IPostsRepo, inserted_post_object: posts.PostInDB, test_db: Database
):
    # 1. Delete post by post_id
    await posts_repo.delete(post_id=inserted_post_object.post_id)

    # 2. Ensure it no longer exists in the database
    post = await test_db.fetch_one(
        "SELECT * FROM posts WHERE posts.post_id = :post_id",
        {"post_id": inserted_post_object.post_id},
    )

    assert not post
