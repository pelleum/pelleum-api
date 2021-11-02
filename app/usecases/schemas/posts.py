from typing import Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, constr, Field

from app.usecases.schemas.request_pagination import MetaData


class Sentiment(str, Enum):
    Bull = "Bull"
    BEAR = "Bear"


class CreatePostRequest(BaseModel):
    """Request from user to create a new post"""

    # NOTE: Would be cool to directly link skin...

    title: Optional[constr(max_length=256)] = Field(
        None,
        description="The post title.",
        example="Bought 5 shares of TSLA at $645.14/share.",
    )
    content: constr(max_length=512) = Field(
        ...,
        description="The post content.",
        example="Pelleum is the future of investing; the retail investing world needs more transparency.",
    )
    asset_symbol: constr(max_length=10) = Field(
        ...,
        description="The symbol for the asset the post (and thesis) is linked to.",
        example="TSLA",
    )
    sentiment: Optional[Sentiment] = Field(
        None, description="The post sentiment.", example="Bull"
    )
    thesis_id: Optional[int] = Field(
        None,
        description="A thesis linked to the post. If left blank, will auto populate with user's thesis for this asset.",
        example="Bull",
    )


class CreatePostRepoAdapter(CreatePostRequest):
    """This model is used to send to the PostsRepo create function"""

    user_id: int
    thesis_id: Optional[int] = None


class PostQueryParams(BaseModel):
    """Object to query posts by; consider adding hashtags"""

    user_id: Optional[int]
    asset_symbol: Optional[str]
    sentiment: Optional[str]
    popularity: Optional[bool]


class PostInDB(CreatePostRequest):
    """Database Model"""

    post_id: int
    user_id: int
    thesis_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class PostResponse(PostInDB):
    """Response returned to user"""


class Posts(BaseModel):
    posts: List[PostResponse]


class ManyPostsResponse(BaseModel):
    records: Optional[Posts]
    meta_data: MetaData
