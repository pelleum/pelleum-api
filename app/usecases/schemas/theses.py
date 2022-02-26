from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, constr

from app.usecases.schemas.request_pagination import MetaData


class Sentiment(str, Enum):
    BULL = "Bull"
    BEAR = "Bear"


class TimeHorizon(str, Enum):
    """implement this when ready"""


class ThesisBase(BaseModel):
    title: constr(max_length=256) = Field(
        ..., description="The thesis title.", example="Pelleum to Change the World."
    )
    content: constr(max_length=30000) = Field(
        ...,
        description="The thesis content.",
        example="Pelleum is the future of investing.",
    )
    asset_symbol: constr(max_length=10) = Field(
        ...,
        description="The symbol for the asset the thesis is being linked to.",
        example="TSLA",
    )
    sentiment: Sentiment = Field(
        ..., description="The thesis sentiment.", example="Bull"
    )


class CreateThesisRequest(ThesisBase):
    """Request from user to create a new thesis"""

    sources: Optional[List[constr(max_length=256)]] = Field(
        None,
        description="The supporting, cited sources an author can optionally include.",
        example=["https://www.pelleum.com", "https://www.youtube.com"],
    )


class UpdateThesisRequest(BaseModel):
    """Request from user to update a thesis"""

    title: Optional[constr(max_length=256)] = Field(
        None, description="The thesis title.", example="Pelleum to Change the World."
    )
    content: Optional[constr(max_length=30000)] = Field(
        None,
        description="The thesis content.",
        example="Pelleum is the future of investing.",
    )
    sources: Optional[List[constr(max_length=256)]] = Field(
        None,
        description="The supporting, cited sources an author can optionally include.",
        example=["https://www.pelleum.com", "https://www.youtube.com"],
    )
    sentiment: Optional[Sentiment] = Field(
        None, description="The thesis sentiment.", example="Bull"
    )
    is_authors_current: Optional[bool] = Field(
        None,
        description="Whether or not this thesis is the author's current linked thesis for this asset.",
        example=True,
    )


class ThesesQueryParams(BaseModel):
    user_id: Optional[int] = Field(
        None,
        description="The user_id of a thesis Author you're querying for.",
        example=1233,
    )
    asset_symbol: Optional[str]
    sentiment: Optional[str]
    popularity: Optional[bool]


class ThesesQueryRepoAdapter(ThesesQueryParams):
    """Used to send to Repo function"""

    requesting_user_id: int = Field(
        ..., description="The user_id of the user that sent the request.", example=1233
    )


class ThesisInDB(ThesisBase):
    """Database Model"""

    thesis_id: int
    user_id: int
    username: str
    sources: Optional[List[str]]
    is_authors_current: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ThesisWithUserReaction(ThesisInDB):
    """Returned from database via join"""

    user_reaction_value: Optional[int] = None


class ThesisResponse(ThesisWithUserReaction):
    """Response returned to user"""


class Theses(BaseModel):
    theses: List[ThesisResponse]


class ManyThesesResponse(BaseModel):
    """Response returned to user"""

    records: Optional[Theses]
    meta_data: MetaData


# Repo Adapters
class CreateThesisRepoAdapter(CreateThesisRequest):
    """This model is used to send to the ThesisRepo create function"""

    user_id: int
    username: str


class UpdateThesisRepoAdapter(UpdateThesisRequest):
    """This model is used to send to the ThesisRepo update function"""

    thesis_id: int
