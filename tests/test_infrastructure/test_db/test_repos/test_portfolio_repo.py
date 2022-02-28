from typing import List

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.schemas import portfolios
from app.usecases.schemas.users import UserInDB

TEST_INSITUTION_ID = "331e8f42-574c-4df6-b2c2-20b348e4ad8a"


@pytest_asyncio.fixture
async def inserted_institution(test_db: Database) -> None:

    await test_db.execute(
        "INSERT INTO account_connections.institutions (institution_id, name) "
        "VALUES (:test_institution_id, 'Robinhood');",
        {"test_institution_id": TEST_INSITUTION_ID},
    )


@pytest_asyncio.fixture
async def inserted_assets(
    inserted_user_object: UserInDB,
    portfolio_repo: IPortfolioRepo,
    inserted_institution: None,
) -> List[portfolios.AssetInDB]:

    assets_symbols = ("TSLA", "BTC", "ETH")

    return [
        await portfolio_repo.create(
            new_asset=portfolios.CreateAssetRepoAdapter(
                user_id=inserted_user_object.user_id,
                institution_id=TEST_INSITUTION_ID,
                name=asset_symbol,
                asset_symbol=asset_symbol,
                quantity=2.58,
            )
        )
        for asset_symbol in assets_symbols
    ]


@pytest.mark.asyncio
async def test_retrieve_assets_with_filter(
    portfolio_repo: IPortfolioRepo, inserted_assets: List[portfolios.AssetInDB]
):

    test_assets = await portfolio_repo.retrieve_assets_with_filter(
        user_id=inserted_assets[0].user_id
    )

    assert len(test_assets) >= 3
    for asset in test_assets:
        assert isinstance(asset, portfolios.AssetInDB)
