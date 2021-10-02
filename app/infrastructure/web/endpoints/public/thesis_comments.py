from typing import Optional
import math

from fastapi import APIRouter, Depends, Body, Path
from fastapi.param_functions import Query
from pydantic import conint

from app.usecases.schemas import thesis_comments
from app.usecases.schemas import users
from app.usecases.schemas.request_pagination import RequestPagination, MetaData
from app.usecases.interfaces.thesis_comments_repo import IThesesCommentsRepo
from app.dependencies import (
    get_thesis_comments_repo,
    get_current_active_user,
    paginate,
    get_thesis_comments_query_params,
)
from app.libraries import pelleum_errors


thesis_comments_router = APIRouter(tags=["Theses Comments"])


@thesis_comments_router.post("/{thesis_id}", status_code=201)
async def create_new_thesis_comment(
    thesis_id: conint(gt=0, lt=100000000000) = Path(...),
    body: thesis_comments.ThesisCommentRequest = Body(...),
    thesis_comments_repo: IThesesCommentsRepo = Depends(get_thesis_comments_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    await thesis_comments_repo.create(
        thesis_id=thesis_id, user_id=authorized_user.user_id, content=body.content
    )


@thesis_comments_router.patch(
    "/{comment_id}",
    status_code=204,
)
async def update_thesis_comment(
    comment_id: conint(gt=0, lt=100000000000) = Path(...),
    body: thesis_comments.UpdateThesisCommentRequest = Body(...),
    thesis_comments_repo: IThesesCommentsRepo = Depends(get_thesis_comments_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    thesis_comment: thesis_comments.ThesisCommentInDB = (
        await thesis_comments_repo.retrieve_thesis_comment_by_id(comment_id=comment_id)
    )

    if not thesis_comment or thesis_comment.user_id != authorized_user.user_id:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied comment_id is invalid."
        ).invalid_resource_id()

    await thesis_comments_repo.update(comment_id=comment_id, content=body.content)


@thesis_comments_router.get(
    "/{comment_id}",
    status_code=200,
    response_model=thesis_comments.ThesisCommentResponse,
)
async def get_thesis_comment(
    comment_id: conint(gt=0, lt=100000000000) = Path(...),
    thesis_comments_repo: IThesesCommentsRepo = Depends(get_thesis_comments_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> thesis_comments.ThesisCommentResponse:

    thesis_comment: thesis_comments.ThesisCommentInDB = (
        await thesis_comments_repo.retrieve_thesis_comment_by_id(comment_id=comment_id)
    )

    if not thesis_comment:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied comment_id is invalid."
        ).invalid_resource_id()

    return thesis_comment


@thesis_comments_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=thesis_comments.ManyThesisCommentsResponse,
)
async def get_many_thesis_comments(
    query_params: thesis_comments.ThesisCommentsQueryParams = Depends(
        get_thesis_comments_query_params
    ),
    thesis_comments_repo: IThesesCommentsRepo = Depends(get_thesis_comments_repo),
    request_pagination: RequestPagination = Depends(paginate),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> thesis_comments.ManyThesisCommentsResponse:

    (
        thesis_comments_list,
        total_thesis_comments_count,
    ) = await thesis_comments_repo.retrieve_many_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    return thesis_comments.ManyThesisCommentsResponse(
        records=thesis_comments.ThesisComments(thesis_comments=thesis_comments_list),
        meta_data=MetaData(
            page=request_pagination.page,
            records_per_page=request_pagination.records_per_page,
            total_records=total_thesis_comments_count,
            total_pages=math.ceil(
                total_thesis_comments_count / request_pagination.records_per_page
            ),
        ),
    )


@thesis_comments_router.delete(
    "/{comment_id}",
    status_code=204,
)
async def delete_thesis_comment(
    comment_id: conint(gt=0, lt=100000000000) = Path(...),
    thesis_comments_repo: IThesesCommentsRepo = Depends(get_thesis_comments_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    thesis_comment: thesis_comments.ThesisCommentInDB = (
        await thesis_comments_repo.retrieve_thesis_comment_by_id(comment_id=comment_id)
    )

    if not thesis_comment or thesis_comment.user_id != authorized_user.user_id:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied comment_id is invalid."
        ).invalid_resource_id()

    await thesis_comments_repo.delete(comment_id=comment_id)
