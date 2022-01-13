from datetime import datetime
from typing import Optional, List

from fastapi import Depends, Query
from pydantic import conint, constr

from app.dependencies import (  # pylint: disable = cyclic-import
    get_posts_repo,
    get_theses_repo,
    get_users_repo,
)
from app.libraries import pelleum_errors
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.usecases.interfaces.user_repo import IUserRepo
from app.usecases.schemas import (
    post_reactions,
    posts,
    rationales,
    theses,
    thesis_reactions,
)


async def get_post_reactions_query_params(  # pylint: disable = too-many-arguments
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    post_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    reaction: Optional[post_reactions.ReactionString] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
) -> post_reactions.PostsReactionsQueryParams:

    if not user_id and not post_id and not reaction and not start_time and not end_time:
        raise await pelleum_errors.PelleumErrors(
            detail="No query parameters were sent. Please send valid query parameters."
        ).invalid_query_params()

    if (start_time and not end_time) or (end_time and not start_time):
        raise await pelleum_errors.PelleumErrors(
            detail="If querying by a date range is desired, please send a valid start_time and end_time."
        ).invalid_query_params()

    query_params_raw = {}

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})

    if post_id:
        post = await posts_repo.retrieve_post_with_filter(post_id=post_id)

        if not post:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied post_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"post_id": post_id})

    if reaction:
        query_params_raw.update({"reaction": reaction})

    if start_time:
        if end_time <= start_time:
            raise await pelleum_errors.PelleumErrors(
                detail="If querying by a date range is desired, please send a valid start_time and end_time (end_time must be greater than start_time)."
            ).invalid_query_params()
        query_params_raw.update(
            {"time_range": {"start_time": start_time, "end_time": end_time}}
        )

    return post_reactions.PostsReactionsQueryParams(**query_params_raw)


async def get_posts_query_params(  # pylint: disable = too-many-arguments
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    asset_symbol: Optional[constr(max_length=10)] = Query(None),
    sentiment: Optional[posts.Sentiment] = Query(None),
    by_popularity: Optional[bool] = Query(None),
    is_post_comment_on: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    is_thesis_comment_on: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
) -> posts.PostQueryParams:

    query_params_raw = {}

    if is_post_comment_on and is_thesis_comment_on:
        raise await pelleum_errors.PelleumErrors(
            detail="Please supply is_thesis_comment_on or is_post_comment_on, "
            "not both."
        ).invalid_query_params()

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})

    if asset_symbol:
        query_params_raw.update({"asset_symbol": asset_symbol})
    if sentiment:
        query_params_raw.update({"sentiment": sentiment})
    if by_popularity:
        query_params_raw.update({"popularity": by_popularity})
    if is_post_comment_on:
        post = await posts_repo.retrieve_post_with_filter(post_id=is_post_comment_on)
        if not post:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied is_post_comment_on ID is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"is_post_comment_on": is_post_comment_on})
    if is_thesis_comment_on:
        thesis = await theses_repo.retrieve_thesis_with_filter(
            thesis_id=is_thesis_comment_on
        )
        if not thesis:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied is_thesis_comment_on ID is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"is_thesis_comment_on": is_thesis_comment_on})

    return posts.PostQueryParams(**query_params_raw)


async def get_theses_query_params(
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    asset_symbol: Optional[constr(max_length=10)] = Query(None),
    sentiment: Optional[theses.Sentiment] = Query(None),
    by_popularity: Optional[bool] = Query(None),
    theses_ids: Optional[List[conint(gt=0, lt=100000000000)]] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
) -> theses.ThesesQueryParams:

    query_params_raw = {}

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})
    if asset_symbol:
        query_params_raw.update({"asset_symbol": asset_symbol})
    if sentiment:
        query_params_raw.update({"sentiment": sentiment})
    if by_popularity:
        query_params_raw.update({"popularity": by_popularity})
    if theses_ids:
        query_params_raw.update({"theses_ids": theses_ids})

    return theses.ThesesQueryParams(**query_params_raw)


async def get_thesis_reactions_query_params(
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    thesis_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    reaction: Optional[thesis_reactions.ReactionString] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
) -> thesis_reactions.ThesisReactionsQueryParams:

    if not user_id and not thesis_id and not reaction:
        raise await pelleum_errors.PelleumErrors(
            detail="No query parameters were sent. Please send valid query parameters."
        ).invalid_query_params()

    query_params_raw = {}

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})
    if thesis_id:
        thesis: theses.ThesisInDB = await theses_repo.retrieve_thesis_with_filter(
            thesis_id=thesis_id
        )

        if not thesis:
            raise await pelleum_errors.PelleumErrors(
                detail="The supplied thesis_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"thesis_id": thesis_id})
    if reaction:
        query_params_raw.update({"reaction": reaction})

    return thesis_reactions.ThesisReactionsQueryParams(**query_params_raw)


async def get_rationales_query_params(
    user_id: conint(gt=0, lt=100000000000) = Query(None),
    asset_symbol: Optional[constr(max_length=10)] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
) -> rationales.RationaleQueryParams:

    user = await users_repo.retrieve_user_with_filter(user_id=user_id)

    if not user:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied user_id is invalid."
        ).invalid_resource_id()

    query_params_raw = {"user_id": user_id}

    if asset_symbol:
        query_params_raw.update({"asset_symbol": asset_symbol})

    return rationales.RationaleQueryParams(**query_params_raw)
