from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, constr

from app.usecases.schemas.request_pagination import MetaData


class PostCommentRequest(BaseModel):
    """Request for user to comment on post"""

    content: constr(max_length=4096) = Field(
        ...,
        description="A comment on a post.",
        example="This is my comment on your post on Pelleum.",
    )


class CreatePostCommentRepoAdapter(BaseModel):
    """Utilized by repo to create new post comment"""

    post_id: int
    user_id: int
    username: str
    content: str


class UpdatePostCommentRequest(PostCommentRequest):
    """Request for user to update post comment"""


class PostCommentInDB(BaseModel):
    """Database Model"""

    comment_id: int
    post_id: int
    user_id: int
    username: str
    content: str
    created_at: datetime
    updated_at: datetime


class PostsCommentsQueryParams(BaseModel):
    """Used to send to PostsCommentsRepo retrieve_many_with_filter"""

    user_id: Optional[int]
    post_id: Optional[int]


class PostCommentResponse(PostCommentInDB):
    """Response returned to user"""


class PostComments(BaseModel):
    post_comments: List[PostCommentResponse]


class ManyPostCommentsResponse(BaseModel):
    """Response returned to user"""

    records: Optional[PostComments]
    meta_data: MetaData
