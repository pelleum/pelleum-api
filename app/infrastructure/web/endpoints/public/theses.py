import math

from fastapi import APIRouter, Body, Depends, Path
from pydantic import conint

from app.dependencies import (
    get_current_active_user,
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

    thesis: theses.ThesisInDB = await theses_repo.retrieve_thesis_with_filter(
        thesis_id=thesis_id
    )

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
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> theses.ThesisResponse:

    thesis = await theses_repo.retrieve_thesis_with_filter(thesis_id=thesis_id)

    if not thesis:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

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
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> theses.ManyThesesResponse:
    """This endpiont returns many theses based on query parameters that were sent to it."""

    query_params_raw = query_params.dict()
    query_params_raw.update({"requesting_user_id": authorized_user.user_id})
    query_params = theses.ThesesQueryRepoAdapter(**query_params_raw)

    # 1. Retrieve theses based on query parameters
    theses_list, total_theses_count = await theses_repo.retrieve_many_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    return theses.ManyThesesResponse(
        records=theses.Theses(theses=theses_list),
        meta_data=MetaData(
            page=request_pagination.page,
            records_per_page=request_pagination.records_per_page,
            total_records=total_theses_count,
            total_pages=math.ceil(
                total_theses_count / request_pagination.records_per_page
            ),
        ),
    )
