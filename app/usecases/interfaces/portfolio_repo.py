from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas import portfolios


class IPortfolioRepo(ABC):
    @abstractmethod
    async def retrieve_asset(
        self,
        asset_id: int = None,
        user_id: int = None,
        institution_id: str = None,
        asset_symbol: str = None,
    ) -> Optional[portfolios.AssetInDB]:
        """Retrieve signle asset"""

    @abstractmethod
    async def retrieve_assets_with_filter(
        self,
        user_id: int,
    ) -> List[portfolios.AssetInDB]:
        """Retrieve all assets in a linked brokerage by user_id"""
