import math
from typing import Union

from fastapi import APIRouter, Body, Depends, Path, Response
from pydantic import conint

from app.dependencies import (
    get_current_active_user,
    get_rationales_query_params,
    get_rationales_repo,
    get_theses_repo,
    get_thesis_reactions_repo,
    paginate,
)
from app.libraries import pelleum_errors
from app.usecases.interfaces.rationales_repo import IRationalesRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.interfaces.thesis_reaction_repo import IThesisReactionRepo
from app.usecases.schemas import rationales, theses, thesis_reactions, users
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

    query_params = rationales.RationaleQueryParams(
        user_id=authorized_user.user_id,
        asset_symbol=thesis.asset_symbol,
        sentiment=thesis.sentiment,
    )
    users_rationales, _ = await rationales_repo.retrieve_many_rationales_with_filter(
        query_params=query_params
    )

    if len(users_rationales) > 9:
        # The maximum amount of rationales has been reached - ask the user if they want to remove one to add this
        response.status_code = 403
        return rationales.MaxRationaleReachedResponse(
            detail=f"The maximium amount of {thesis.sentiment} theses for {thesis.asset_symbol} has been reached for this user."
        )

    return await rationales_repo.create(
        thesis_id=body.thesis_id, user_id=authorized_user.user_id
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
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    rationales_repo: IRationalesRepo = Depends(get_rationales_repo),
    thesis_reaction_repo: IThesisReactionRepo = Depends(get_thesis_reactions_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> rationales.ManyRationalesResponse:
    """This endpoint returns many rationales based on supplied query parameters."""

    # 1. Retrieve rationales
    (
        retrieved_rationales,
        rationales_count,
    ) = await rationales_repo.retrieve_many_rationales_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    # 2. Retrieve theses (based on retrieved rationales)
    list_of_thesis_ids = [rationale.thesis_id for rationale in retrieved_rationales]
    theses_list = await theses_repo.retrieve_theses_by_ids(
        theses_ids=list_of_thesis_ids
    )
    theses_response = theses.Theses(theses=theses_list)

    # 3. Obtiain the requesting user's liked posts with the time range of retrieved posts
    if theses_list:
        newest_thesis_created_at = theses_list[0].created_at
        oldest_thesis_created_at = theses_list[-1].created_at

        (
            theses_reactions_list,
            _,
        ) = await thesis_reaction_repo.retrieve_many_with_filter(
            query_params=thesis_reactions.ThesisReactionsQueryParams(
                user_id=authorized_user.user_id,
                time_range=thesis_reactions.TimeRange(
                    start_time=oldest_thesis_created_at,
                    end_time=newest_thesis_created_at,
                ),
            ),
            page_number=request_pagination.page,
            page_size=request_pagination.records_per_page,
        )
        # 4. Update thesis objects with like data where necessary
        # O(N) = O(|theses_response.theses|) * O(|theses_reactions_list|)
        # This can get pretty high if the user likes a lot of theses...
        # Would be more perfomant is we outsourced this to the frontend as we scale
        # Backend work = O(N) * requests from user, which can get really high
        for thesis in theses_response.theses:
            for reaction in theses_reactions_list:
                if thesis.thesis_id == reaction.thesis_id:
                    thesis.user_reaction_value = reaction.reaction

    return rationales.ManyRationalesResponse(
        records=theses_response,
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
    status_code=204,
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
