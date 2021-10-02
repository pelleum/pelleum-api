from typing import Optional
import math

from fastapi import APIRouter, Depends, Body, Path
from fastapi.param_functions import Query
from pydantic import conint

from app.usecases.schemas import thesis_reactions, theses
from app.usecases.schemas import users
from app.usecases.schemas.request_pagination import RequestPagination, MetaData
from app.usecases.interfaces.thesis_reaction_repo import IThesisReactionRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.dependencies import (
    get_thesis_reactions_repo,
    get_theses_repo,
    get_current_active_user,
    paginate,
    get_thesis_reactions_query_params,
)
from app.libraries import pelleum_errors


thesis_reactions_router = APIRouter(tags=["Thesis Reactions"])


@thesis_reactions_router.post("/{thesis_id}", status_code=201)
async def create_thesis_reaction(
    thesis_id: conint(gt=0, lt=100000000000) = Path(...),
    body: thesis_reactions.ThesisReactionRequest = Body(...),
    thesis_reactions_repo: IThesisReactionRepo = Depends(get_thesis_reactions_repo),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    thesis: theses.ThesisInDB = await theses_repo.retrieve_thesis_with_filter(
        thesis_id=thesis_id
    )

    if not thesis:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

    thesis_reaction = thesis_reactions.ThesisReactionRepoAdapter(
        thesis_id=thesis_id, user_id=authorized_user.user_id, reaction=body.reaction
    )

    await thesis_reactions_repo.create(thesis_reaction=thesis_reaction)


@thesis_reactions_router.patch("/{thesis_id}", status_code=204)
async def update_thesis_reaction(
    thesis_id: conint(gt=0, lt=100000000000) = Path(...),
    body: thesis_reactions.UpdateThesisReactionRequest = Body(...),
    thesis_reactions_repo: IThesisReactionRepo = Depends(get_thesis_reactions_repo),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    thesis: theses.ThesisInDB = await theses_repo.retrieve_thesis_with_filter(
        thesis_id=thesis_id
    )

    if not thesis:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

    updated_reaction = thesis_reactions.ThesisReactionRepoAdapter(
        thesis_id=thesis_id, user_id=authorized_user.user_id, reaction=body.reaction
    )

    await thesis_reactions_repo.update(thesis_reaction_update=updated_reaction)


@thesis_reactions_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=thesis_reactions.ManyThesesReactionsResponse,
)
async def get_many_thesis_reactions(
    query_params: thesis_reactions.ThesisReactionsQueryParams = Depends(
        get_thesis_reactions_query_params
    ),
    request_pagination: RequestPagination = Depends(paginate),
    thesis_reactions_repo: IThesisReactionRepo = Depends(get_thesis_reactions_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> thesis_reactions.ManyThesesReactionsResponse:

    (
        theses_reactions_list,
        theses_reactions_count,
    ) = await thesis_reactions_repo.retrieve_many_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    return thesis_reactions.ManyThesesReactionsResponse(
        records=thesis_reactions.ThesesReactions(
            theses_reactions=theses_reactions_list
        ),
        meta_data=MetaData(
            page=request_pagination.page,
            records_per_page=request_pagination.records_per_page,
            total_records=theses_reactions_count,
            total_pages=math.ceil(
                theses_reactions_count / request_pagination.records_per_page
            ),
        ),
    )


@thesis_reactions_router.delete(
    "/{thesis_id}",
    status_code=204,
)
async def delete_thesis_reaction(
    thesis_id: str = Path(...),
    thesis_reactions_repo: IThesisReactionRepo = Depends(get_thesis_reactions_repo),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    thesis: theses.ThesisInDB = await theses_repo.retrieve_thesis_with_filter(
        thesis_id=thesis_id
    )

    if not thesis or thesis.user_id != authorized_user.user_id:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied thesis_id is invalid."
        ).invalid_resource_id()

    await thesis_reactions_repo.delete(
        thesis_id=thesis_id, user_id=authorized_user.user_id
    )
