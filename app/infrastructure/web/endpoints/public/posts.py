import math

from fastapi import APIRouter, Body, Depends, Path
from pydantic import conint

from app.dependencies import (
    get_current_active_user,
    get_post_reactions_repo,
    get_posts_query_params,
    get_posts_repo,
    get_theses_repo,
    paginate,
)
from app.libraries import pelleum_errors
from app.usecases.interfaces.post_reaction_repo import IPostReactionRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.schemas import post_reactions, posts, users
from app.usecases.schemas.request_pagination import MetaData, RequestPagination

posts_router = APIRouter(tags=["Posts"])


@posts_router.post(
    "",
    status_code=201,
    response_model=posts.PostResponse,
)
async def create_new_post(
    body: posts.CreatePostRequest = Body(...),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> posts.PostResponse:
    """Creates a new post. This can be a stand-alone post, a post comment, or a
    thesis comment."""

    if body.is_thesis_comment_on and body.is_post_comment_on:
        raise await pelleum_errors.PelleumErrors(
            detail="Both is_thesis_comment_on and is_post_comment_on were supplied. If "
            "commenting, please supply one or the other, not both."
        ).invalid_query_params()

    if body.is_post_comment_on:
        post = await posts_repo.retrieve_post_with_filter(
            post_id=body.is_post_comment_on
        )
        if not post:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied is_post_comment_on ID is invalid."
            ).invalid_resource_id()

    if body.is_thesis_comment_on:
        thesis = await theses_repo.retrieve_thesis_with_filter(
            thesis_id=body.is_thesis_comment_on
        )
        if not thesis:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied is_thesis_comment_on ID is invalid."
            ).invalid_resource_id()

    create_post_request_raw = body.dict()
    create_post_request_raw.update(
        {"user_id": authorized_user.user_id, "username": authorized_user.username}
    )

    new_post = posts.CreatePostRepoAdapter(**create_post_request_raw)

    return await posts_repo.create(new_post=new_post)

@posts_router.get(
    "/{post_id}",
    status_code=200,
    response_model=posts.PostResponse,
)
async def get_post(
    post_id: conint(gt=0, lt=100000000000) = Path(...),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> posts.PostResponse:

    post = await posts_repo.retrieve_post_with_filter(post_id=post_id)

    if not post:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    return post


@posts_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=posts.ManyPostsResponse,
)
async def get_many_posts(
    query_params: posts.PostQueryParams = Depends(get_posts_query_params),
    request_pagination: RequestPagination = Depends(paginate),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    post_reactions_repo: IPostReactionRepo = Depends(get_post_reactions_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> posts.ManyPostsResponse:
    """This endpoint returns many posts based on query parameters that were sent to it."""

    # 1. Retrieve posts based on query parameters
    posts_list, total_theses_count = await posts_repo.retrieve_many_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    posts_response = posts.Posts(posts=posts_list)

    # 2. Obtiain the requesting user's liked posts with the time range of retrieved posts
    if posts_list:
        newest_post_created_at = posts_list[0].created_at
        oldest_post_created_at = posts_list[-1].created_at

        (posts_reactions_list, _) = await post_reactions_repo.retrieve_many_with_filter(
            query_params=post_reactions.PostsReactionsQueryParams(
                user_id=authorized_user.user_id,
                time_range=post_reactions.TimeRange(
                    start_time=oldest_post_created_at, end_time=newest_post_created_at
                ),
            ),
            page_number=request_pagination.page,
            page_size=request_pagination.records_per_page,
        )

        # 3. Update post objects with like data where necessary
        # O(N) = O(|posts_response.posts|) * O(|posts_reactions_list|)
        # This can get pretty high if the user likes a lot of posts...
        # Would be more perfomant is we outsourced this to the frontend as we scale
        # Backend work = O(N) * requests from user, which can get really high
        for post in posts_response.posts:
            for reaction in posts_reactions_list:
                if post.post_id == reaction.post_id:
                    post.user_reaction_value = reaction.reaction

    return posts.ManyPostsResponse(
        records=posts_response,
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
async def delete_post(
    post_id: conint(gt=0, lt=100000000000) = Path(...),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    post = await posts_repo.retrieve_post_with_filter(post_id=int(post_id))

    if not post or post.user_id != authorized_user.user_id:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    await posts_repo.delete(post_id=post_id)
