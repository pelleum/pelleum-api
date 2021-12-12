from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.usecases.schemas.request_pagination import MetaData


class Reaction(int, Enum):
    LIKE = 1


class ReactionString(str, Enum):
    LIKE = "1"


class TimeRange(BaseModel):
    start_time: datetime
    end_time: datetime


class PostReactionBase(BaseModel):
    """This model is the base of a post reaction"""

    user_id: int
    post_id: int
    reaction: int


class PostReactionRequest(BaseModel):
    """Request from user to like a post"""

    reaction: Reaction = Field(
        ...,
        description="A 1 signifies a like.",
        example=1,
    )


class PostReactionRepoAdapter(PostReactionBase):
    """This model is used to send to the PostReactionRepo create function"""


class PostsReactionsQueryParams(BaseModel):
    """This model is used to send to the PostReactionRepo retrieve_many_with_filter function"""

    user_id: Optional[int]
    post_id: Optional[int]
    reaction: Optional[int]
    time_range: Optional[TimeRange]


class PostReactionInDB(PostReactionBase):
    """Database Model"""

    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class PostsReactions(BaseModel):
    posts_reactions: List[PostReactionInDB]


class ManyPostsReactionsResponse(BaseModel):
    """Response returned to user"""

    records: Optional[PostsReactions]
    meta_data: MetaData
