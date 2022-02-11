import math
from typing import Union

from fastapi import APIRouter, Body, Depends, Path, Response
from pydantic import conint

from app.dependencies import (
    get_current_active_user,
    get_rationales_query_params,
    get_rationales_repo,
    get_theses_repo,
    paginate,
)
from app.libraries import pelleum_errors
from app.settings import settings
from app.usecases.interfaces.rationales_repo import IRationalesRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.schemas import rationales, theses, users
from app.usecases.schemas.request_pagination import MetaData, RequestPagination

rationale_router = APIRouter(tags=["Rationales"])


@rationale_router.post(
    "",
    status_code=201,
    response_model=Union[
        rationales.RationaleResponse, rationales.MaxRationaleReachedResponse
    ],
)
async def add_thesis_to_rationales(
    response: Response,
    body: rationales.AddRationaleRequest = Body(...),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    rationales_repo: IRationalesRepo = Depends(get_rationales_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> Union[rationales.RationaleResponse, rationales.MaxRationaleReachedResponse]:
    """Adds a thesis to a user's "rationale library"."""

    thesis = await theses_repo.retrieve_thesis_with_filter(thesis_id=body.thesis_id)

    if not thesis:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

    query_params = rationales.RationaleQueryRepoAdapter(
        user_id=authorized_user.user_id,
        asset_symbol=thesis.asset_symbol,
        sentiment=thesis.sentiment,
    )
    users_rationales, _ = await rationales_repo.retrieve_many_rationales_with_filter(
        query_params=query_params
    )

    if len(users_rationales) >= settings.max_rationale_limit:
        # The maximum amount of rationales has been reached - ask the user if they want to remove one to add this
        response.status_code = 403
        return rationales.MaxRationaleReachedResponse(
            detail=f"The maximium amount of {thesis.sentiment} theses for {thesis.asset_symbol} has been reached for this user.",
        )

    rationale_with_thesis = await rationales_repo.create(
        thesis_id=body.thesis_id, user_id=authorized_user.user_id
    )

    # 2. Format the data
    rationale_raw = rationale_with_thesis.dict()
    thesis_object_raw = {}
    for key, value in rationale_raw.items():
        if key[0:7] == "thesis_" and value is not None:
            thesis_object_raw[key[7:]] = value

    return rationales.RationaleResponse(
        thesis=theses.ThesisInDB(**thesis_object_raw) if thesis_object_raw else None,
        **rationale_raw,
    )


@rationale_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=rationales.ManyRationalesResponse,
)
async def get_many_rationales(
    query_params: rationales.RationaleQueryParams = Depends(
        get_rationales_query_params
    ),
    request_pagination: RequestPagination = Depends(paginate),
    rationales_repo: IRationalesRepo = Depends(get_rationales_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> rationales.ManyRationalesResponse:
    """This endpoint returns many rationales based on supplied query parameters."""

    # 1. if no user_id is supplied, use requesting user, else use suplied user
    query_params_raw = query_params.dict()
    query_params = rationales.RationaleQueryRepoAdapter(**query_params_raw)
    if not query_params.user_id:
        query_params.user_id = authorized_user.user_id

    # 1. Retrieve rationales
    (
        retrieved_rationales,
        rationales_count,
    ) = await rationales_repo.retrieve_many_rationales_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    # 2. Format the data
    formatted_rationales = []
    for rationale in retrieved_rationales:
        rationale_raw = rationale.dict()
        thesis_object_raw = {}
        for key, value in rationale_raw.items():
            if key[0:7] == "thesis_" and value is not None:
                thesis_object_raw[key[7:]] = value
        formatted_rationales.append(
            rationales.RationaleResponse(
                thesis=theses.ThesisInDB(**thesis_object_raw)
                if thesis_object_raw
                else None,
                **rationale_raw,
            )
        )

    return rationales.ManyRationalesResponse(
        records=rationales.Rationales(rationales=formatted_rationales),
        meta_data=MetaData(
            page=request_pagination.page,
            records_per_page=request_pagination.records_per_page,
            total_records=rationales_count,
            total_pages=math.ceil(
                rationales_count / request_pagination.records_per_page
            ),
        ),
    )


@rationale_router.delete(
    "/{rationale_id}",
    status_code=200,
)
async def delete_rationale(
    rationale_id: conint(gt=0, lt=100000000000) = Path(...),
    rationales_repo: IRationalesRepo = Depends(get_rationales_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:
    """Deletes a rationale from a user's "rationale library"."""

    rationale = await rationales_repo.retrieve_rationale_with_filter(
        rationale_id=rationale_id
    )

    if not rationale or rationale.user_id != authorized_user.user_id:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied rationale_id is invalid."
        ).invalid_resource_id()

    await rationales_repo.delete(rationale_id=rationale_id)
