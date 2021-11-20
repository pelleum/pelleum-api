from typing import List

from fastapi import APIRouter, Depends, Path
from pydantic import conint

from app.usecases.schemas import portfolios
from app.usecases.schemas import users
from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.dependencies import get_portfolio_repo, get_current_active_user
from app.libraries import pelleum_errors

portfolio_router = APIRouter(tags=["User Portfolio"])


@portfolio_router.get(
    "/{user_id}",
    status_code=200,
    response_model=portfolios.UserAssetsResponse,
)
async def get_portfolio_assets(
    user_id: conint(gt=0, lt=100000000000) = Path(...),
    portfolio_repo: IPortfolioRepo = Depends(get_portfolio_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> portfolios.UserAssetsResponse:
    """Retrieves assets owned by a Pelleum user."""

    portfolio = await portfolio_repo.retrieve_portfolio(user_id=user_id)

    if not portfolio:
        raise await pelleum_errors.PelleumErrors(
            detail="Invalid user_id."
        ).invalid_resource_id()

    user_assets = await portfolio_repo.retrieve_assets_with_filter(
        portfolio_id=portfolio.portfolio_id
    )

    return portfolios.UserAssetsResponse(records=user_assets)
