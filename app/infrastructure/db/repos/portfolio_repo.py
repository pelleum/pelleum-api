from typing import List, Optional

from databases import Database
from sqlalchemy import and_, delete, desc

from app.infrastructure.db.models.portfolio import ASSETS, PORTFOLIOS
from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.schemas import portfolios


class PortfolioRepo(IPortfolioRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create_portfolio(self, user_id: int) -> None:
        """Creates new portfolio"""

        portfolio_insert_statement = PORTFOLIOS.insert().values(user_id=user_id)

        await self.db.execute(portfolio_insert_statement)

    async def retrieve_portfolio(
        self, user_id: str
    ) -> Optional[portfolios.PortfolioInDB]:
        """Retrieve portfolio by user_id"""

        query = PORTFOLIOS.select().where(PORTFOLIOS.c.user_id == user_id)

        result = await self.db.fetch_one(query)
        if result:
            return portfolios.PortfolioInDB(**result)

    async def retrieve_all_portfolios(self) -> List[portfolios.PortfolioInDB]:
        """Retrieve all Pelleum portfolios"""

        query = PORTFOLIOS.select().order_by(desc(PORTFOLIOS.c.created_at))

        query_results = await self.db.fetch_all(query)
        return [portfolios.PortfolioInDB(**result) for result in query_results]

    async def retrieve_asset(
        self,
        asset_id: int = None,
        portfolio_id: int = None,
        institution_id: str = None,
        asset_symbol: str = None,
    ) -> Optional[portfolios.AssetInDB]:
        """Retrieve signle asset"""
        # NOTE: Might not need this function... It's here just in case

        conditions = []

        if asset_id:
            conditions.append(ASSETS.c.asset_id == asset_id)

        if portfolio_id:
            conditions.append(ASSETS.c.portfolio_id == portfolio_id)

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
        portfolio_id: int,
    ) -> List[portfolios.AssetInDB]:
        """Retrieve all assets in a linked brokerage by portfolio_id"""

        conditions = []

        if portfolio_id:
            conditions.append(ASSETS.c.portfolio_id == portfolio_id)

        query = ASSETS.select().where(and_(*conditions))
        results = await self.db.fetch_all(query)
        return [portfolios.AssetInDB(**result) for result in results]

    async def delete_asset(self, asset_id: int) -> None:
        """Delete asset"""

        delete_statement = delete(ASSETS).where(ASSETS.c.asset_id == asset_id)

        await self.db.execute(delete_statement)
