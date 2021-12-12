from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.usecases.schemas.request_pagination import MetaData


class Reaction(int, Enum):
    LIKE = 1
    DISLIKE = -1


class ReactionString(str, Enum):
    LIKE = "1"
    DISLIKE = "-1"


class TimeRange(BaseModel):
    start_time: datetime
    end_time: datetime


class ThesisReactionBase(BaseModel):
    """This model is the base of a thesis reaction"""

    user_id: int
    thesis_id: int
    reaction: int


class ThesisReactionRequest(BaseModel):
    """Request from user to like a thesis"""

    reaction: Reaction = Field(
        ...,
        description="A 1 signifies a like. A -1 signifies a dislike.",
        example=1,
    )


class UpdateThesisReactionRequest(BaseModel):
    """Request from user to like a thesis"""

    reaction: Reaction = Field(
        ...,
        description="A 1 signifies a like. A -1 signifies a dislike.",
        example=1,
    )


class ThesisReactionRepoAdapter(ThesisReactionBase):
    """This model is used to send to the ThesisReactionRepo create function"""


class ThesisReactionsQueryParams(BaseModel):
    """This model is used to send to the ThesisReactionRepo retrieve_many_with_filter function"""

    user_id: Optional[int]
    thesis_id: Optional[int]
    reaction: Optional[int]
    time_range: Optional[TimeRange]


class ThesisReactionInDB(ThesisReactionBase):
    """Database Model"""

    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ThesesReactions(BaseModel):
    theses_reactions: List[ThesisReactionInDB]


class ManyThesesReactionsResponse(BaseModel):
    """Response returned to user"""

    records: Optional[ThesesReactions]
    meta_data: MetaData
