from pydantic import BaseModel, constr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.usecases.schemas.request_pagination import MetaData


class Sentiment(str, Enum):
    BULL = "bull"
    BEAR = "bear"


class TimeHorizon(str, Enum):
    # TODO: implement this when ready
    pass


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
        description="The asset symbol for the asset the thesis is being linked to.",
        example="TSLA",
    )
    sentiment: Sentiment = Field(
        ..., description="The thesis sentiment.", example="bull"
    )


class CreateThesisRequest(ThesisBase):
    """Request from user to create a new thesis"""

    sources: Optional[List[constr(max_length=256)]] = Field(
        ...,
        description="The supporting, cited sources an author can optionally include.",
        example=["https://www.pelleum.com", "https://www.youtube.com"],
    )


class UpdateThesisRequest(BaseModel):
    """Request from user to update thesis"""

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
        None, description="The thesis sentiment.", example="bull"
    )
    is_authors_current: Optional[bool] = Field(
        None,
        description="Whether or not this thesis is the author's current linked thesis for this asset.",
        example=True,
    )


class CreateThesisRepoAdapter(CreateThesisRequest):
    """This model is used to send to the ThesisRepo create function"""

    user_id: int


class UpdateThesisRepoAdapter(UpdateThesisRequest):
    """This model is used to send to the ThesisRepo update function"""

    thesis_id: int


class ThesesQueryParams(BaseModel):
    user_id: Optional[int]
    asset_symbol: Optional[str]
    sentiment: Optional[str]
    popularity: Optional[bool]


class ThesisInDB(ThesisBase):
    """Database Model"""

    thesis_id: int
    user_id: int
    sources: Optional[List[str]]
    is_authors_current: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class ThesisResponse(ThesisInDB):
    """Response returned to user"""


class Theses(BaseModel):
    theses: List[ThesisResponse]


class ManyThesesResponse(BaseModel):
    records: Optional[Theses]
    meta_data: MetaData


class ManyThesesRepoAdapter(BaseModel):
    theses: List[ThesisInDB]
    total_theses: int
