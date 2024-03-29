from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from app.usecases.schemas.posts import PostWithReactionData
from app.usecases.schemas.theses import ThesisInDB


class EventType(str, Enum):
    COMMENT = "COMMENT"
    POST_REACTION = "POST_REACTION"
    THESIS_REACTION = "THESIS_REACTION"


class NewEventRepoAdapter(BaseModel):
    type: EventType
    user_to_notify: int
    user_who_fired_event: int
    affected_post_id: Optional[int]
    affected_thesis_id: Optional[int]
    comment_id: Optional[int]


class NotificationInDb(BaseModel):
    """Database Model"""

    notification_id: int
    user_to_notify: int
    user_who_fired_event: int
    event_id: int
    acknowledged: bool
    created_at: datetime
    updated_at: datetime


class EventInDb(BaseModel):
    """Database Model"""

    event_id: int
    type: str
    affected_post_id: Optional[int]
    affected_thesis_id: Optional[int]
    comment_id: Optional[int]


class NotificationDbInfo(EventInDb):
    """Notifications joined events joined users"""

    acknowledged: bool
    notification_id: int
    username: str
    user_id: int


class NotifcationResponseObject(BaseModel):
    event_id: int
    type: str
    acknowledged: bool
    affected_post_id: Optional[int]
    affected_thesis_id: Optional[int]
    notification_id: int
    user_id: int
    username: str
    comment: Optional[PostWithReactionData]
    post: Optional[PostWithReactionData]
    thesis: Optional[ThesisInDB]


class NotificationsResponse(BaseModel):
    """Same as NotificationDbInfo"""

    notifications: List[NotifcationResponseObject]
