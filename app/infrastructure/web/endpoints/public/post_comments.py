import math

from fastapi import APIRouter, Depends, Body, Path
from pydantic import conint

from app.usecases.schemas import post_comments
from app.usecases.schemas import users
from app.usecases.schemas.request_pagination import RequestPagination, MetaData
from app.usecases.interfaces.post_comments_repo import IPostsCommentsRepo

from app.dependencies import (
    get_post_comments_repo,
    get_current_active_user,
    paginate,
    get_post_comments_query_params,
)
from app.libraries import pelleum_errors


post_comments_router = APIRouter(tags=["Posts Comments"])


@post_comments_router.post("/{post_id}", status_code=201)
async def create_new_post_comment(
    post_id: conint(gt=0, lt=100000000000) = Path(...),
    body: post_comments.PostCommentRequest = Body(...),
    post_comments_repo: IPostsCommentsRepo = Depends(get_post_comments_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    await post_comments_repo.create(
        comment_info=post_comments.CreatePostCommentRepoAdapter(
            post_id=post_id,
            user_id=authorized_user.user_id,
            username=authorized_user.username,
            content=body.content,
        )
    )


@post_comments_router.patch(
    "/{comment_id}",
    status_code=204,
)
async def update_post_comment(
    comment_id: conint(gt=0, lt=100000000000) = Path(...),
    body: post_comments.UpdatePostCommentRequest = Body(...),
    post_comments_repo: IPostsCommentsRepo = Depends(get_post_comments_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    post_comment: post_comments.PostCommentInDB = (
        await post_comments_repo.retrieve_post_comment_by_id(comment_id=comment_id)
    )

    if not post_comment or post_comment.user_id != authorized_user.user_id:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied comment_id is invalid."
        ).invalid_resource_id()

    await post_comments_repo.update(comment_id=comment_id, content=body.content)


@post_comments_router.get(
    "/{comment_id}",
    status_code=200,
    response_model=post_comments.PostCommentResponse,
)
async def get_post_comment(
    comment_id: conint(gt=0, lt=100000000000) = Path(...),
    post_comments_repo: IPostsCommentsRepo = Depends(get_post_comments_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> post_comments.PostCommentResponse:

    post_comment: post_comments.PostCommentInDB = (
        await post_comments_repo.retrieve_post_comment_by_id(comment_id=comment_id)
    )

    if not post_comment:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied comment_id is invalid."
        ).invalid_resource_id()

    return post_comment


@post_comments_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=post_comments.ManyPostCommentsResponse,
)
async def get_many_post_comments(
    query_params: post_comments.PostsCommentsQueryParams = Depends(
        get_post_comments_query_params
    ),
    post_comments_repo: IPostsCommentsRepo = Depends(get_post_comments_repo),
    request_pagination: RequestPagination = Depends(paginate),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> post_comments.ManyPostCommentsResponse:

    (
        post_comments_list,
        total_post_comments_count,
    ) = await post_comments_repo.retrieve_many_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    return post_comments.ManyPostCommentsResponse(
        records=post_comments.PostComments(post_comments=post_comments_list),
        meta_data=MetaData(
            page=request_pagination.page,
            records_per_page=request_pagination.records_per_page,
            total_records=total_post_comments_count,
            total_pages=math.ceil(
                total_post_comments_count / request_pagination.records_per_page
            ),
        ),
    )


@post_comments_router.delete(
    "/{comment_id}",
    status_code=204,
)
async def delete_post_comment(
    comment_id: conint(gt=0, lt=100000000000) = Path(...),
    post_comments_repo: IPostsCommentsRepo = Depends(get_post_comments_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    post_comment: post_comments.PostCommentInDB = (
        await post_comments_repo.retrieve_post_comment_by_id(comment_id=comment_id)
    )

    if not post_comment or post_comment.user_id != authorized_user.user_id:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied comment_id is invalid."
        ).invalid_resource_id()

    await post_comments_repo.delete(comment_id=comment_id)
