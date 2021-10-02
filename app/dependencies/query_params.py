from typing import Optional

from fastapi import Query, Depends
from pydantic import conint, constr

from app.usecases.schemas import (
    post_comments,
    post_reactions,
    posts,
    theses,
    thesis_comments,
    thesis_reactions,
)
from app.usecases.interfaces.user_repo import IUserRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.interfaces.theses_repo import IThesesRepo
from app.dependencies import get_users_repo, get_posts_repo, get_theses_repo  # pylint: disable = cyclic-import
from app.libraries import pelleum_errors


async def get_post_comments_query_params(
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    post_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
) -> post_comments.PostsCommentsQueryParams:

    if not user_id and not post_id:
        raise pelleum_errors.no_supplied_query_params

    query_params_raw = {}

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})

    if post_id:
        post = await posts_repo.retrieve_post_with_filter(post_id=post_id)

        if not post:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied post_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"post_id": post_id})

    return post_comments.PostsCommentsQueryParams(**query_params_raw)


async def get_post_reactions_query_params(
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    post_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    reaction: Optional[post_reactions.ReactionString] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
) -> post_reactions.PostsReactionsQueryParams:

    if not user_id and not post_id and not reaction:
        raise pelleum_errors.no_supplied_query_params

    query_params_raw = {}

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})

    if post_id:
        post = await posts_repo.retrieve_post_with_filter(post_id=post_id)

        if not post:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied post_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"post_id": post_id})

    if reaction:
        query_params_raw.update({"reaction": reaction})

    return post_reactions.PostsReactionsQueryParams(**query_params_raw)


async def get_posts_query_params(
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    asset_symbol: Optional[constr(max_length=10)] = Query(None),
    sentiment: Optional[posts.Sentiment] = Query(None),
    by_popularity: Optional[bool] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
) -> posts.PostQueryParams:

    if not user_id and not asset_symbol and not sentiment and not by_popularity:
        raise pelleum_errors.no_supplied_query_params

    query_params_raw = {}

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})

    if asset_symbol:
        query_params_raw.update({"asset_symbol": asset_symbol})
    if sentiment:
        query_params_raw.update({"sentiment": sentiment})
    if by_popularity:
        query_params_raw.update({"popularity": by_popularity})

    return posts.PostQueryParams(**query_params_raw)


async def get_theses_query_params(
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    asset_symbol: Optional[constr(max_length=10)] = Query(None),
    sentiment: Optional[theses.Sentiment] = Query(None),
    by_popularity: Optional[bool] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
) -> theses.ThesesQueryParams:

    if not user_id and not asset_symbol and not sentiment and not by_popularity:
        raise pelleum_errors.no_supplied_query_params

    query_params_raw = {}

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})
    if asset_symbol:
        query_params_raw.update({"asset_symbol": asset_symbol})
    if sentiment:
        query_params_raw.update({"sentiment": sentiment})
    if by_popularity:
        query_params_raw.update({"popularity": by_popularity})

    return theses.ThesesQueryParams(**query_params_raw)


async def get_thesis_comments_query_params(
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    thesis_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    by_popularity: Optional[bool] = Query(None),      # pylint: disable = unused-argument
    users_repo: IUserRepo = Depends(get_users_repo),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
) -> thesis_comments.ThesisCommentsQueryParams:

    if not user_id and not thesis_id:
        raise pelleum_errors.no_supplied_query_params

    query_params_raw = {}

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})
    if thesis_id:
        thesis: theses.ThesisInDB = await theses_repo.retrieve_thesis_with_filter(
            thesis_id=thesis_id
        )

        if not thesis:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied thesis_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"thesis_id": thesis_id})

    return thesis_comments.ThesisCommentsQueryParams(**query_params_raw)


async def get_thesis_reactions_query_params(
    user_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    thesis_id: Optional[conint(gt=0, lt=100000000000)] = Query(None),
    reaction: Optional[thesis_reactions.ReactionString] = Query(None),
    users_repo: IUserRepo = Depends(get_users_repo),
    theses_repo: IThesesRepo = Depends(get_theses_repo),
) -> thesis_reactions.ThesisReactionsQueryParams:

    if not user_id and not thesis_id and not reaction:
        raise pelleum_errors.no_supplied_query_params

    query_params_raw = {}

    if user_id:
        user = await users_repo.retrieve_user_with_filter(user_id=user_id)

        if not user:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied user_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"user_id": user_id})
    if thesis_id:
        thesis: theses.ThesisInDB = await theses_repo.retrieve_thesis_with_filter(
            thesis_id=thesis_id
        )

        if not thesis:
            raise await pelleum_errors.InvalidResourceId(
                detail="The supplied thesis_id is invalid."
            ).invalid_resource_id()

        query_params_raw.update({"thesis_id": thesis_id})
    if reaction:
        query_params_raw.update({"reaction": reaction})

    return thesis_reactions.ThesisReactionsQueryParams(**query_params_raw)
