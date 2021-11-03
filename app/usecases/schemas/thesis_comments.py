from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, constr

from app.usecases.schemas.request_pagination import MetaData


class ThesisCommentRequest(BaseModel):
    """Request for user to comment on thesis"""

    content: constr(max_length=4096) = Field(
        ...,
        description="A comment on a thesis.",
        example="This is my comment on your thesis on Pelleum.",
    )


class UpdateThesisCommentRequest(ThesisCommentRequest):
    """Request for user to update thesis comment"""


class CreateThesisCommentRepoAdapter(BaseModel):
    """Utilized by repo to create new post comment"""

    thesis_id: int
    user_id: int
    username: str
    content: str


class ThesisCommentInDB(BaseModel):
    """Database Model"""

    comment_id: int
    thesis_id: int
    user_id: int
    username: str
    content: str
    created_at: datetime
    updated_at: datetime


class ThesisCommentsQueryParams(BaseModel):
    """Used to send to ThesesCommentsRepo retrieve_many_with_filter"""

    user_id: Optional[int]
    thesis_id: Optional[int]


class ThesisCommentResponse(ThesisCommentInDB):
    """Response returned to user"""


class ThesisComments(BaseModel):
    thesis_comments: List[ThesisCommentResponse]


class ManyThesisCommentsResponse(BaseModel):
    """Response returned to user"""

    records: Optional[ThesisComments]
    meta_data: MetaData
