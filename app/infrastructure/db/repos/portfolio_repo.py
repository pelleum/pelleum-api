from typing import List, Optional

from databases import Database
from sqlalchemy import and_, delete

from app.infrastructure.db.models.public.portfolio import ASSETS
from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.schemas import portfolios


class PortfolioRepo(IPortfolioRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, new_asset: portfolios.CreateAssetRepoAdapter
    ) -> portfolios.AssetInDB:
        """This function only exists for unit tests -- this repo doesn't handle asset
        creation"""

        asset_insert_statement = ASSETS.insert().values(
            user_id=new_asset.user_id,
            institution_id=new_asset.institution_id,
            thesis_id=new_asset.thesis_id,
            asset_symbol=new_asset.asset_symbol,
            name=new_asset.name,
            position_value=new_asset.position_value,
            quantity=new_asset.quantity,
            skin_rating=new_asset.skin_rating,
            average_buy_price=new_asset.average_buy_price,
            total_contribution=new_asset.total_contribution,
            is_up_to_date=True,
        )

        asset_id = await self.db.execute(asset_insert_statement)
        return await self.retrieve_asset(asset_id=asset_id)

    async def retrieve_asset(
        self,
        asset_id: int = None,
        user_id: int = None,
        institution_id: str = None,
        asset_symbol: str = None,
    ) -> Optional[portfolios.AssetInDB]:
        """Retrieve signle asset"""

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
