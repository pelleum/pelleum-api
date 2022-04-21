import math
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Path
from pydantic import conint

from app.dependencies import (
    get_block_data,
    get_current_active_user,
    get_notifications_repo,
    get_optional_user,
    get_posts_query_params,
    get_posts_repo,
    get_theses_repo,
    paginate,
)
from app.libraries import pelleum_errors
from app.usecases.interfaces.notifications_repo import INotificationsRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.schemas import notifications, posts, theses, users
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
    notifications_repo: INotificationsRepo = Depends(get_notifications_repo),
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

        event = notifications.NewEventRepoAdapter(
            type=notifications.EventType.COMMENT,
            user_to_notify=post.user_id,
            user_who_fired_event=authorized_user.user_id,
            affected_post_id=post.post_id,
        )

    if body.is_thesis_comment_on:
        thesis = await theses_repo.retrieve_thesis_with_filter(
            thesis_id=body.is_thesis_comment_on
        )
        if not thesis:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied is_thesis_comment_on ID is invalid."
            ).invalid_resource_id()

        event = notifications.NewEventRepoAdapter(
            type=notifications.EventType.COMMENT,
            user_to_notify=thesis.user_id,
            user_who_fired_event=authorized_user.user_id,
            affected_thesis_id=thesis.thesis_id,
        )

    create_post_request_raw = body.dict()
    create_post_request_raw.update(
        {"user_id": authorized_user.user_id, "username": authorized_user.username}
    )

    # Save post in database
    created_post = await posts_repo.create(
        new_post=posts.CreatePostRepoAdapter(**create_post_request_raw)
    )

    # If post was a comment, insert comment notification
    if body.is_post_comment_on or body.is_thesis_comment_on:
        event.comment_id = created_post.post_id
        await notifications_repo.create(new_event=event)

    return created_post


@posts_router.get(
    "/{post_id}",
    status_code=200,
    response_model=posts.PostResponse,
)
async def get_post(
    post_id: conint(gt=0, lt=100000000000) = Path(...),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    user_block_data: users.BlockData = Depends(get_block_data),
    optional_user: Optional[users.UserInDB] = Depends(get_optional_user),
) -> posts.PostResponse:

    # 1. Retrieve the post (if not optional user, user_id = 1... something that does not exist)
    post = await posts_repo.retrieve_post_with_filter(
        post_id=post_id, user_id=optional_user.user_id if optional_user else -1
    )

    if not post:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    # 2. If user is blocked, prevent access
    if (
        post.user_id in user_block_data.user_blocks
        or post.user_id in user_block_data.user_blocked_by
    ):
        raise await pelleum_errors.PelleumErrors(
            detail="You're account has been blocked by the user of this resource."
        ).access_forbidden()

    # 3. Format the post
    post_raw = post.dict()
    thesis_object_raw = {}
    for key, value in post_raw.items():
        if key[0:7] == "thesis_" and value is not None:
            thesis_object_raw[key[7:]] = value
    return posts.PostResponse(
        thesis=theses.ThesisInDB(**thesis_object_raw) if thesis_object_raw else None,
        **post_raw
    )


@posts_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=posts.ManyPostsResponse,
)
async def get_many_posts(
    query_params: posts.PostQueryParams = Depends(get_posts_query_params),
    request_pagination: RequestPagination = Depends(paginate),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    user_block_data: users.BlockData = Depends(get_block_data),
    optional_user: users.UserInDB = Depends(get_optional_user),
) -> posts.ManyPostsResponse:
    """This endpoint returns many posts based on query parameters that were sent to it."""

    query_params_raw = query_params.dict()
    query_params_raw.update(
        {"requesting_user_id": optional_user.user_id if optional_user else -1}
    )
    query_params = posts.PostQueryRepoAdapter(**query_params_raw)

    # 1. Retrieve posts based on query parameters
    posts_list, post_count = await posts_repo.retrieve_many_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    # 2. For each post, retrieve comments and update post object along the way
    posts_with_replies = await get_and_add_replies(
        posts_list=posts_list,
        posts_repo=posts_repo,
        user_id=optional_user.user_id if optional_user else -1,
        user_block_data=user_block_data,
        get_max_levels=True
        if query_params.is_post_comment_on or query_params.is_thesis_comment_on
        else False,
    )

    # 3. Format the data
    formatted_posts = []
    for post in posts_with_replies:
        post_raw = post.dict()
        thesis_object_raw = {}
        for key, value in post_raw.items():
            if key[0:7] == "thesis_" and value is not None:
                thesis_object_raw[key[7:]] = value
        formatted_posts.append(
            posts.PostResponse(
                thesis=theses.ThesisInDB(**thesis_object_raw)
                if thesis_object_raw
                else None,
                **post_raw
            )
        )

    return posts.ManyPostsResponse(
        records=posts.Posts(posts=formatted_posts),
        meta_data=MetaData(
            page=request_pagination.page,
            records_per_page=request_pagination.records_per_page,
            total_records=post_count,
            total_pages=math.ceil(post_count / request_pagination.records_per_page),
        ),
    )


@posts_router.delete(
    "/{post_id}",
    status_code=200,
)
async def delete_post(
    post_id: conint(gt=0, lt=100000000000) = Path(...),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    post = await posts_repo.retrieve_post_with_filter(post_id=post_id)

    if not post or post.user_id != authorized_user.user_id:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    await posts_repo.delete(post_id=post_id)


async def get_and_add_replies(
    posts_list: List[posts.PostInfoFromDB],
    posts_repo: IPostsRepo,
    user_id: int,
    user_block_data: users.BlockData,
    get_max_levels=False,
) -> List[posts.PostInfoFromDB]:
    """This function grabs up to 3 levels of replies (if get_max_levels is True).
    Else, it will grab 1 level or replies"""

    for post in posts_list:
        if post.comment_count > 0:
            first_order_replies, _ = await posts_repo.retrieve_many_with_filter(
                query_params=posts.PostQueryRepoAdapter(
                    requesting_user_id=user_id, is_post_comment_on=post.post_id
                ),
                page_number=1,
                page_size=15,
            )
            # Filter blocked content and save
            filtered_first_order_replies = await filter_blocked_content(
                posts_list=first_order_replies, user_block_data=user_block_data
            )
            post.replies = filtered_first_order_replies

            # For PostDetail, grab all levels. For feed, stop after one level of replies
            if get_max_levels:
                for reply in post.replies:
                    if reply.comment_count > 0:
                        (
                            second_order_replies,
                            _,
                        ) = await posts_repo.retrieve_many_with_filter(
                            query_params=posts.PostQueryRepoAdapter(
                                requesting_user_id=user_id,
                                is_post_comment_on=reply.post_id,
                            ),
                            page_number=1,
                            page_size=5,
                        )

                        # Filter blocked content and save
                        filtered_second_order_replies = await filter_blocked_content(
                            posts_list=second_order_replies,
                            user_block_data=user_block_data,
                        )
                        reply.replies = filtered_second_order_replies

                        for reply in reply.replies:
                            if reply.comment_count > 0:
                                (
                                    third_order_replies,
                                    _,
                                ) = await posts_repo.retrieve_many_with_filter(
                                    query_params=posts.PostQueryRepoAdapter(
                                        requesting_user_id=user_id,
                                        is_post_comment_on=reply.post_id,
                                    ),
                                    page_number=1,
                                    page_size=5,
                                )

                                # Filter blocked content and save
                                filtered_third_order_replies = (
                                    await filter_blocked_content(
                                        posts_list=third_order_replies,
                                        user_block_data=user_block_data,
                                    )
                                )
                                reply.replies = filtered_third_order_replies

    return posts_list


async def filter_blocked_content(
    posts_list: List[posts.PostInfoFromDB], user_block_data: users.BlockData
) -> List[posts.PostInfoFromDB]:
    """Removes blocked content"""

    if user_block_data.user_blocks or user_block_data.user_blocked_by:
        filtered_posts = []
        for post in posts_list:
            if (
                post.user_id not in user_block_data.user_blocks
                and post.user_id not in user_block_data.user_blocked_by
            ):
                filtered_posts.append(post)
        return filtered_posts
    else:
        return posts_list
