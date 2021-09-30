from fastapi import APIRouter, Depends, Body, Path
from fastapi.param_functions import Query
from app.usecases.schemas import theses
from app.usecases.schemas import users
from app.usecases.schemas.request_pagination import RequestPagination, MetaData
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.dependencies import get_theses_repo, get_current_active_user, paginate
from app.libraries import pelleum_errors
from typing import List, Optional
import math

theses_router = APIRouter(tags=["theses"])


@theses_router.post(
    "",
    status_code=201,
    response_model=theses.ThesisResponse,
)
async def create_new_thesis(
    body: theses.CreateThesisRequest = Body(...),
    thesis_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> theses.ThesisResponse:

    if len(body.sources) > 10:
        raise pelleum_errors.array_too_long

    create_thesis_request_raw = body.dict()
    create_thesis_request_raw.update({"user_id": authorized_user.user_id})

    thesis = theses.CreateThesisRepoAdapter(**create_thesis_request_raw)

    newly_created_thesis: theses.ThesisInDB = await thesis_repo.create(thesis=thesis)

    return newly_created_thesis


@theses_router.patch(
    "/{thesis_id}",
    status_code=200,
    response_model=theses.ThesisResponse,
)
async def update_thesis(
    thesis_id: str = Path(...),
    body: theses.UpdateThesisRequest = Body(...),
    thesis_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> theses.ThesisResponse:

    if len(body.sources) > 10:
        raise pelleum_errors.array_too_long

    thesis: theses.ThesisInDB = await thesis_repo.retrieve_thesis_with_filter(
        thesis_id=int(thesis_id)
    )

    if not thesis or thesis.user_id != authorized_user.user_id:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

    update_thesis_request_raw = body.dict()
    update_thesis_request_raw.update({"thesis_id": thesis_id})

    updated_thesis = theses.UpdateThesisRepoAdapter(**update_thesis_request_raw)

    updated_thesis: theses.ThesisInDB = await thesis_repo.update(
        updated_thesis=updated_thesis
    )

    return updated_thesis


@theses_router.get(
    "/{thesis_id}",
    status_code=200,
    response_model=theses.ThesisResponse,
)
async def get_thesis(
    thesis_id: str = Path(...),
    thesis_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> theses.ThesisResponse:

    thesis: theses.ThesisInDB = await thesis_repo.retrieve_thesis_with_filter(
        thesis_id=int(thesis_id)
    )

    if not thesis:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

    return thesis


@theses_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=theses.ManyThesesResponse,
)
async def get_many_theses(
    by_user_id: Optional[bool] = Query(None),
    asset_symbol: Optional[str] = Query(None),
    sentiment: Optional[theses.Sentiment] = Query(None),
    by_popularity: Optional[bool] = Query(None),
    request_pagination: RequestPagination = Depends(paginate),
    thesis_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> theses.ManyThesesResponse:

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

    query_params = theses.ThesesQueryParams(**query_params_raw)

    theses_list, total_theses_count = await thesis_repo.retrieve_many_with_filter(
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
