from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.usecases.schemas.request_pagination import MetaData
from app.usecases.schemas.theses import ThesisWithUserReaction


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


class ThesisWithRationaleId(ThesisWithUserReaction):
    """Returned from database join"""

    rationale_id: int
    rationale_user_id: int


class RationaleResponse(ThesisWithRationaleId):
    """Individual rationale returned to user"""


class MaxRationaleReachedResponse(BaseModel):
    """This is the response model that's sent when the max
    amount of rationales have been added to the user's rationale library"""

    detail: str


class Rationales(BaseModel):
    rationales: List[RationaleResponse]


class ManyRationalesResponse(BaseModel):
    records: Optional[Rationales]
    meta_data: MetaData
