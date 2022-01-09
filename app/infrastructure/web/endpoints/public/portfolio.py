from fastapi import APIRouter, Depends, Path
from pydantic import conint

from app.dependencies import get_current_active_user, get_portfolio_repo
from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.schemas import portfolios, users

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

    user_assets = await portfolio_repo.retrieve_assets_with_filter(
        user_id=authorized_user.user_id  # This would need to change to user_id
    )

    return portfolios.UserAssetsResponse(records=user_assets)
