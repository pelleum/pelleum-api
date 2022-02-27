from typing import List

import pytest
import pytest_asyncio
from databases import Database
from httpx import AsyncClient

from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.schemas.portfolios import (
    AssetInDB,
    CreateAssetRepoAdapter,
    UserAssetsResponse,
)
from app.usecases.schemas.users import UserInDB

TEST_INSITUTION_ID = "a08da358-44ef-4c27-852f-4f4313772332"


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
) -> List[AssetInDB]:

    assets_symbols = ("TSLA", "BTC", "ETH")

    return [
        await portfolio_repo.create(
            new_asset=CreateAssetRepoAdapter(
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
async def test_get_portfolio_assets(
    test_client: AsyncClient, inserted_assets: List[AssetInDB]
) -> None:

    endpoint = f"/public/portfolio/{inserted_assets[0].user_id}"

    response = await test_client.get(endpoint)

    response_data = response.json()
    expected_response_fields = [field for field in AssetInDB.__fields__]

    # Assertions
    assert response.status_code == 200
    assert "records" in response_data
    assert len(response_data.get("records")) == len(inserted_assets)
    for asset in response_data.get("records"):
        for key in asset:
            assert key in expected_response_fields
