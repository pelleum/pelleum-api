from typing import Optional
import math

from fastapi import APIRouter, Depends, Body, Path
from fastapi.param_functions import Query
from pydantic import conint

from app.usecases.schemas import post_reactions, posts
from app.usecases.schemas import users
from app.usecases.schemas.request_pagination import RequestPagination, MetaData
from app.usecases.interfaces.post_reaction_repo import IPostReactionRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.dependencies import (
    get_post_reactions_repo,
    get_posts_repo,
    get_current_active_user,
    paginate,
)
from app.libraries import pelleum_errors


post_reactions_router = APIRouter(tags=["Post Reactions"])


@post_reactions_router.post("/{post_id}", status_code=201)
async def create_post_reaction(
    post_id: conint(gt=0, lt=100000000000) = Path(...),
    body: post_reactions.PostReactionRequest = Body(...),
    post_reactions_repo: IPostReactionRepo = Depends(get_post_reactions_repo),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    post: posts.PostInDB = await posts_repo.retrieve_post_with_filter(post_id=post_id)

    if not post:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    post_reaction = post_reactions.PostReactionRepoAdapter(
        post_id=post_id, user_id=authorized_user.user_id, reaction=body.reaction
    )

    await post_reactions_repo.create(post_reaction=post_reaction)


@post_reactions_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=post_reactions.ManyPostsReactionsResponse,
)
async def get_many_posts(
    by_user_id: Optional[bool] = Query(None),
    post_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    reaction: Optional[post_reactions.ReactionString] = Query(None),
    request_pagination: RequestPagination = Depends(paginate),
    post_reactions_repo: IPostReactionRepo = Depends(get_post_reactions_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> post_reactions.ManyPostsReactionsResponse:

    if not by_user_id and not post_id and not reaction:
        raise pelleum_errors.no_supplied_query_params

    query_params_raw = {}

    if by_user_id:
        query_params_raw.update({"user_id": authorized_user.user_id})
    if post_id:
        query_params_raw.update({"post_id": post_id})
    if reaction:
        query_params_raw.update({"reaction": reaction})

    query_params = post_reactions.PostsReactionsQueryParams(**query_params_raw)

    (
        posts_reactions_list,
        posts_reactions_count,
    ) = await post_reactions_repo.retrieve_many_with_filter(
        query_params=query_params,
        page_number=request_pagination.page,
        page_size=request_pagination.records_per_page,
    )

    return post_reactions.ManyPostsReactionsResponse(
        records=post_reactions.PostsReactions(posts_reactions=posts_reactions_list),
        meta_data=MetaData(
            page=request_pagination.page,
            records_per_page=request_pagination.records_per_page,
            total_records=posts_reactions_count,
            total_pages=math.ceil(
                posts_reactions_count / request_pagination.records_per_page
            ),
        ),
    )


@post_reactions_router.delete(
    "/{post_id}",
    status_code=204,
)
async def delete_post_reaction(
    post_id: str = Path(...),
    post_reactions_repo: IPostReactionRepo = Depends(get_post_reactions_repo),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    post: posts.PostInDB = await posts_repo.retrieve_post_with_filter(
        post_id=int(post_id)
    )

    if not post or post.user_id != authorized_user.user_id:
        raise await pelleum_errors.InvalidResourceId(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    await post_reactions_repo.delete(
        post_id=int(post_id), user_id=authorized_user.user_id
    )