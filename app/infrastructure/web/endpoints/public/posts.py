from fastapi import APIRouter, Depends, Body, Path
from fastapi.param_functions import Query
from app.usecases.schemas import posts
from app.usecases.schemas import users
from app.usecases.schemas.request_pagination import RequestPagination, MetaData
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.dependencies import (
    get_posts_repo,
    get_posts_repo,
    get_current_active_user,
    paginate,
)
from app.libraries import pelleum_errors
from typing import List, Optional
import math

posts_router = APIRouter(tags=["posts"])


@posts_router.post(
    "",
    status_code=201,
)
async def create_new_feed_post(
    body: posts.CreatePostRequest = Body(...),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    create_feed_post_request_raw = body.dict()
    create_feed_post_request_raw.update({"user_id": authorized_user.user_id})
    # TODO: grab author's current thesis for the linked asset, for now hard code it to 1
    create_feed_post_request_raw.update({"thesis_id": 4})

    new_feed_post = posts.CreatePostRepoAdapter(**create_feed_post_request_raw)

    await posts_repo.create(new_feed_post=new_feed_post)


@posts_router.get(
    "/{post_id}",
    status_code=200,
    response_model=posts.PostResponse,
)
async def get_feed_post(
    post_id: str = Path(...),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> posts.PostResponse:

    post: posts.PostInDB = await posts_repo.retrieve_post_with_filter(
        post_id=int(post_id)
    )

    if not post:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    return post


@posts_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=posts.ManyPostsResponse,
)
async def get_many_posts(
    by_user_id: Optional[bool] = Query(None),
    asset_symbol: Optional[str] = Query(None),
    sentiment: Optional[posts.Sentiment] = Query(None),
    by_popularity: Optional[bool] = Query(None),
    request_pagination: RequestPagination = Depends(paginate),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> posts.ManyPostsResponse:

    if not by_user_id and not asset_symbol and not sentiment and not by_popularity:
        raise pelleum_errors.no_supplied_query_params

    query_params_raw = {}

    if by_user_id:
        query_params_raw.update({"user_id": authorized_user.user_id})
    if asset_symbol:
        query_params_raw.update({"asset_symbol": asset_symbol})
    if sentiment:
        query_params_raw.update({"sentiment": sentiment})
    if by_popularity:
        query_params_raw.update({"popularity": by_popularity})

    query_params = posts.PostQueryParams(**query_params_raw)

    theses_list, total_theses_count = await posts_repo.retrieve_many_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    return posts.ManyPostsResponse(
        records=posts.Posts(posts=theses_list),
        meta_data=MetaData(
            page=request_pagination.page,
            records_per_page=request_pagination.records_per_page,
            total_records=total_theses_count,
            total_pages=math.ceil(
                total_theses_count / request_pagination.records_per_page
            ),
        ),
    )


@posts_router.delete(
    "/{post_id}",
    status_code=204,
)
async def delete_feed_post(
    post_id: str = Path(...),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> posts.PostResponse:

    post: posts.PostInDB = await posts_repo.retrieve_post_with_filter(
        post_id=int(post_id)
    )

    if not post or post.user_id != authorized_user.user_id:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    await posts_repo.delete(post_id=int(post_id))
