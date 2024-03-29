import math

from fastapi import APIRouter, Body, Depends, Path, Response
from pydantic import conint
from starlette.status import HTTP_204_NO_CONTENT

from app.dependencies import (
    get_block_data,
    get_current_active_user,
    get_optional_user,
    get_theses_query_params,
    get_theses_repo,
    paginate,
)
from app.libraries import pelleum_errors
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.schemas import theses, users
from app.usecases.schemas.request_pagination import MetaData, RequestPagination

theses_router = APIRouter(tags=["Theses"])


@theses_router.post(
    "",
    status_code=201,
    response_model=theses.ThesisResponse,
)
async def create_new_thesis(
    body: theses.CreateThesisRequest = Body(...),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> theses.ThesisResponse:
    """Create a thesis."""

    if body.sources:
        if len(body.sources) > 10:
            raise await pelleum_errors.PelleumErrors().array_too_long()

    create_thesis_request_raw = body.dict()
    create_thesis_request_raw.update(
        {"user_id": authorized_user.user_id, "username": authorized_user.username}
    )

    thesis = theses.CreateThesisRepoAdapter(**create_thesis_request_raw)

    newly_created_thesis = await theses_repo.create(thesis=thesis)

    return newly_created_thesis


@theses_router.patch(
    "/{thesis_id}",
    status_code=200,
    response_model=theses.ThesisResponse,
)
async def update_thesis(
    thesis_id: conint(gt=0, lt=100000000000) = Path(...),
    body: theses.UpdateThesisRequest = Body(...),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> theses.ThesisResponse:
    """Update a thesis."""

    if len(body.sources) > 10:
        raise await pelleum_errors.PelleumErrors().array_too_long()

    thesis = await theses_repo.retrieve_thesis_with_filter(thesis_id=thesis_id)

    if not thesis or thesis.user_id != authorized_user.user_id:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

    update_thesis_request_raw = body.dict()
    update_thesis_request_raw.update({"thesis_id": thesis_id})

    updated_thesis = theses.UpdateThesisRepoAdapter(**update_thesis_request_raw)

    updated_thesis = await theses_repo.update(updated_thesis=updated_thesis)

    return updated_thesis


@theses_router.get(
    "/{thesis_id}",
    status_code=200,
    response_model=theses.ThesisResponse,
)
async def get_thesis(
    thesis_id: conint(gt=0, lt=100000000000) = Path(...),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    user_block_data: users.BlockData = Depends(get_block_data),
    optional_user: users.UserInDB = Depends(get_optional_user),
) -> theses.ThesisResponse:

    thesis = await theses_repo.retrieve_thesis_with_reaction(
        thesis_id=thesis_id, user_id=optional_user.user_id if optional_user else -1
    )

    # 1. Ensure resource exists
    if not thesis:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

    # 2. If user is blocked, prevent access
    if (
        thesis.user_id in user_block_data.user_blocks
        or thesis.user_id in user_block_data.user_blocked_by
    ):
        raise await pelleum_errors.PelleumErrors(
            detail="You're account has been blocked by the user of this resource."
        ).access_forbidden()

    return thesis


@theses_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=theses.ManyThesesResponse,
)
async def get_many_theses(
    query_params: theses.ThesesQueryParams = Depends(get_theses_query_params),
    request_pagination: RequestPagination = Depends(paginate),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    user_block_data: users.BlockData = Depends(get_block_data),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> theses.ManyThesesResponse:
    """This endpiont returns many theses based on query parameters that were sent to it."""

    query_params_raw = query_params.dict()
    query_params_raw.update({"requesting_user_id": authorized_user.user_id})
    query_params = theses.ThesesQueryRepoAdapter(**query_params_raw)

    # 1. Retrieve theses based on query parameters
    theses_list, theses_count = await theses_repo.retrieve_many_with_filter(
        query_params=query_params,
        user_id=authorized_user.user_id,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    # 2. Remove blocked content
    if user_block_data.user_blocks or user_block_data.user_blocked_by:
        filtered_theses = []
        for post in theses_list:
            if (
                post.user_id not in user_block_data.user_blocks
                and post.user_id not in user_block_data.user_blocked_by
            ):
                filtered_theses.append(post)
    else:
        filtered_theses = theses_list

    return theses.ManyThesesResponse(
        records=theses.Theses(theses=filtered_theses),
        meta_data=MetaData(
            page=request_pagination.page,
            records_per_page=request_pagination.records_per_page,
            total_records=theses_count,
            total_pages=math.ceil(theses_count / request_pagination.records_per_page),
        ),
    )


@theses_router.delete(
    "/{thesis_id}",
    status_code=HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_thesis(
    thesis_id: conint(gt=0, lt=100000000000) = Path(...),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    thesis = await theses_repo.retrieve_thesis_with_filter(thesis_id=thesis_id)

    # 1. Ensure resource exists
    if not thesis or thesis.user_id != authorized_user.user_id:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

    await theses_repo.delete(thesis_id=thesis_id)
