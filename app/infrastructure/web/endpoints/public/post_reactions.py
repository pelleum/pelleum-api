import math

from fastapi import APIRouter, Body, Depends, Path, Response
from pydantic import conint
from starlette.status import HTTP_204_NO_CONTENT

from app.dependencies import (
    get_current_active_user,
    get_notifications_repo,
    get_post_reactions_query_params,
    get_post_reactions_repo,
    get_posts_repo,
    paginate,
)
from app.libraries import pelleum_errors
from app.usecases.interfaces.notifications_repo import INotificationsRepo
from app.usecases.interfaces.post_reaction_repo import IPostReactionRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.schemas import notifications, post_reactions, users
from app.usecases.schemas.request_pagination import MetaData, RequestPagination

post_reactions_router = APIRouter(tags=["Post Reactions"])


@post_reactions_router.post("/{post_id}", status_code=201)
async def create_post_reaction(
    post_id: conint(gt=0, lt=100000000000) = Path(...),
    body: post_reactions.PostReactionRequest = Body(...),
    post_reactions_repo: IPostReactionRepo = Depends(get_post_reactions_repo),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    notifications_repo: INotificationsRepo = Depends(get_notifications_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    post = await posts_repo.retrieve_post_with_filter(post_id=post_id)

    if not post:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    post_reaction = post_reactions.PostReactionRepoAdapter(
        post_id=post_id, user_id=authorized_user.user_id, reaction=body.reaction
    )

    # Like the post
    await post_reactions_repo.create(post_reaction=post_reaction)

    # Insert Notification
    await notifications_repo.create(
        new_event=notifications.NewEventRepoAdapter(
            type=notifications.EventType.POST_REACTION,
            user_to_notify=post.user_id,
            user_who_fired_event=authorized_user.user_id,
            affected_post_id=post.post_id,
        )
    )


@post_reactions_router.get(
    "/retrieve/many",
    status_code=200,
    response_model=post_reactions.ManyPostsReactionsResponse,
)
async def get_many_post_reactions(
    query_params: post_reactions.PostsReactionsQueryParams = Depends(
        get_post_reactions_query_params
    ),
    request_pagination: RequestPagination = Depends(paginate),
    post_reactions_repo: IPostReactionRepo = Depends(get_post_reactions_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> post_reactions.ManyPostsReactionsResponse:
    """This is a 'Swiss army knife' endpoint in the sense that it returns
    a list of post reactions based on the query parameters supplied to it."""

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
    status_code=HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_post_reaction(
    post_id: conint(gt=0, lt=100000000000) = Path(...),
    post_reactions_repo: IPostReactionRepo = Depends(get_post_reactions_repo),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:

    post = await posts_repo.retrieve_post_with_filter(post_id=post_id)

    if not post:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied post_id is invalid."
        ).invalid_resource_id()

    await post_reactions_repo.delete(
        post_id=int(post_id), user_id=authorized_user.user_id
    )
