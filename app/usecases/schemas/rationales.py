from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.usecases.schemas.request_pagination import MetaData
from app.usecases.schemas.theses import ThesisInDB


class AddRationaleRequest(BaseModel):
    """JSON body in request to add a rationale"""

    thesis_id: int = Field(
        ...,
        description="The thesis_id the user wants to add to his or her rationale library.",
        example="2345",
    )


class RationaleQueryParams(BaseModel):
    """Object to query rationales by"""

    user_id: Optional[int]
    asset_symbol: Optional[str]
    thesis_id: Optional[int]
    sentiment: Optional[str]


class RationaleQueryRepoAdapter(RationaleQueryParams):
    """Used to send to Repo function"""

    requesting_user_id: int = Field(
        ..., description="The user_id of the user that sent the request.", example=1233
    )


class RationaleInDb(BaseModel):
    """Database Model"""

    rationale_id: int
    thesis_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime




class RationaleWithThesis(RationaleInDb):
    """Returned from database join"""

    thesis_title: Optional[str]
    thesis_content: Optional[str]
    thesis_asset_symbol: Optional[str]
    thesis_sentiment: Optional[str]
    thesis_thesis_id: Optional[int]
    thesis_user_id: Optional[int]
    thesis_username: Optional[str]
    thesis_is_authors_current: Optional[bool]
    thesis_sources: Optional[List[str]]
    thesis_created_at: Optional[datetime]
    thesis_updated_at: Optional[datetime]




class RationaleResponse(RationaleInDb):
    """Individual rationale returned to user"""
    thesis: Optional[ThesisInDB]


class MaxRationaleReachedResponse(BaseModel):
    """This is the response model that's sent when the max
    amount of rationales have been added to the user's rationale library"""

    detail: str


class Rationales(BaseModel):
    rationales: List[RationaleResponse]


class ManyRationalesResponse(BaseModel):
    records: Optional[Rationales]
    meta_data: MetaData
