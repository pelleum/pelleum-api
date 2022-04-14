from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


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

    notification_id: int
    user_id: int


class NotificationsResponse(BaseModel):
    """Same as NotificationDbInfo"""

    notifications: List[NotificationDbInfo]
