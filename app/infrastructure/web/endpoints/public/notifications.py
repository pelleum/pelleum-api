from fastapi import APIRouter, Depends, Path
from pydantic import conint

from app.dependencies import get_current_active_user, get_notifications_repo, get_posts_repo
from app.libraries import pelleum_errors
from app.usecases.interfaces.notifications_repo import INotificationsRepo
from app.usecases.interfaces.posts_repo import IPostsRepo
from app.usecases.schemas import notifications, users

notifications_router = APIRouter(tags=["Notifications"])


@notifications_router.get(
    "",
    status_code=200,
    response_model=notifications.NotificationsResponse,
)
async def get_user_notifications(
    notifications_repo: INotificationsRepo = Depends(get_notifications_repo),
    posts_repo: IPostsRepo = Depends(get_posts_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> notifications.NotificationsResponse:
    """Retrieves all of a user's unacknowledged notifications."""

    user_notifications = await notifications_repo.retrieve_many(
        user_id=authorized_user.user_id
    )

    notificatations_with_comments = []
    for notification in user_notifications:
        notification_raw = notification.dict()
        if notification.comment_id:
            comment_object = await posts_repo.retrieve_post_with_filter(post_id=notification.comment_id, user_id=authorized_user.user_id)
            notification_raw["comment"] = comment_object
        notificatations_with_comments.append(notifications.NotifcationResponseObject(**notification_raw))
        

    return notifications.NotificationsResponse(notifications=notificatations_with_comments)


@notifications_router.patch(
    "/{notification_id}",
    status_code=200,
    response_model=notifications.NotificationsResponse,
)
async def acknowledge_notification(
    notifications_repo: INotificationsRepo = Depends(get_notifications_repo),
    notification_id: conint(gt=0, lt=100000000000) = Path(...),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> notifications.NotificationsResponse:
    """Acknowledges a notification."""

    notification = await notifications_repo.retrieve_single(
        notification_id=notification_id
    )

    if not notification:
        raise await pelleum_errors.PelleumErrors(
            detail="The supplied notification_id is invalid."
        ).invalid_resource_id()

    await notifications_repo.update(notification_id=notification_id)
