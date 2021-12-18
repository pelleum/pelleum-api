from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AssetInDB(BaseModel):
    """Database Model"""

    asset_id: int = Field(
        ...,
        description="The unique identifier of a Pelleum user's individually owned asset",
        example=1,
    )
    portfolio_id: int = Field(
        ..., description="Unique identifier for Pelleum user's portfolio.", example=1
    )
    institution_id: str = Field(
        ...,
        description="The unique identifer for a Pelleum supported institution.",
        example="d74e2cf4-a4ea-4268-88b3-14bfcdf7c199",
    )
    thesis_id: Optional[int] = Field(
        None,
        description="The unique identifier of the asset's linked thesis.",
        example=1,
    )
    asset_symbol: str = Field(..., description="The asset's symbol.", example="TSLA")
    name: Optional[str] = Field(None, description="The asset's name.", example="Tesla")
    quantity: float = Field(
        ..., description="The number of asset units owned.", example=135.24
    )
    position_value: Optional[float] = Field(
        None,
        description="The US dollar value of the owned asset position.",
        example=1234.56,
    )
    skin_rating: Optional[float] = Field(
        None, description="The Pelleum assigned 'skin rating'.", example=9.8
    )
    average_buy_price: Optional[float] = Field(
        None,
        description="The average (USD) price that the user bought the asset at.",
        example=134.35,
    )
    total_contribution: Optional[float] = Field(
        None,
        description="The sum of all the particular asset's purchases in USD.",
        example=12345.34,
    )
    is_up_to_date: bool = Field(
        ...,
        description="Whether or not the asset resource is up to date with the linked brokerage.",
        example=True,
    )
    update_errors: Optional[str] = Field(
        None,
        description="An error during the periodic asset update process.",
        example="There was an error.",
    )
    created_at: datetime = Field(
        ...,
        description="The time and date that the asset was created in our database.",
        example="2021-10-19 04:56:14.02395",
    )
    updated_at: datetime = Field(
        ...,
        description="The time and date that the asset was updated in our database.",
        example="2021-10-19 04:56:14.02395",
    )


class PortfolioInDB(BaseModel):
    """Database Model"""

    portfolio_id: int = Field(
        ...,
        description="The unique identifier of a user's Pelleum portfolio.",
        example=3473873,
    )
    user_id: int = Field(
        ...,
        description="The user ID associated with this Pelleum portfolio.",
        example=3454,
    )
    aggregated_value: Optional[float] = Field(
        None,
        description="The total value of the user's Pelleum portfolio in US dollars.",
        example=785943,
    )
    created_at: datetime = Field(
        ...,
        description="The time and date that the asset was created in our database.",
        example="2021-10-19 04:56:14.02395",
    )
    updated_at: datetime = Field(
        ...,
        description="The time and date that the asset was updated in our database.",
        example="2021-10-19 04:56:14.02395",
    )


############### Responses ###############
class UserAssetsResponse(BaseModel):
    records: List[AssetInDB]
