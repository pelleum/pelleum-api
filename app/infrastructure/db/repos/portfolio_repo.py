from typing import List, Optional

from databases import Database
from sqlalchemy import and_, delete

from app.infrastructure.db.models.portfolio import ASSETS
from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.schemas import portfolios


class PortfolioRepo(IPortfolioRepo):
    def __init__(self, db: Database):
        self.db = db

    async def retrieve_asset(
        self,
        asset_id: int = None,
        user_id: int = None,
        institution_id: str = None,
        asset_symbol: str = None,
    ) -> Optional[portfolios.AssetInDB]:
        """Retrieve signle asset"""
        # NOTE: Might not need this function... It's here just in case

        conditions = []

        if asset_id:
            conditions.append(ASSETS.c.asset_id == asset_id)

        if user_id:
            conditions.append(ASSETS.c.user_id == user_id)

        if asset_symbol:
            conditions.append(ASSETS.c.asset_symbol == asset_symbol)

        if institution_id:
            conditions.append(ASSETS.c.institution_id == institution_id)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_asset()"
            )

        query = ASSETS.select().where(and_(*conditions))
        result = await self.db.fetch_one(query)
        return portfolios.AssetInDB(**result) if result else None

    async def retrieve_assets_with_filter(
        self,
        user_id: int,
    ) -> List[portfolios.AssetInDB]:
        """Retrieve all assets in a linked brokerage by user_id"""

        conditions = []

        if user_id:
            conditions.append(ASSETS.c.user_id == user_id)

        query = ASSETS.select().where(and_(*conditions))
        results = await self.db.fetch_all(query)
        return [portfolios.AssetInDB(**result) for result in results]

    async def delete_asset(self, asset_id: int) -> None:
        """Delete asset"""

        delete_statement = delete(ASSETS).where(ASSETS.c.asset_id == asset_id)

        await self.db.execute(delete_statement)
