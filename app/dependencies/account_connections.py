import aiohttp
from fastapi import Depends

from app.dependencies import get_client_session
from app.infrastructure.clients.account_connections import AccountConnectionsClient
from app.settings import settings
from app.usecases.interfaces.clients.account_connections import (
    IAccountConnectionsClient,
)


async def get_account_connections_client(
    client_session: aiohttp.client.ClientSession = Depends(get_client_session),
) -> IAccountConnectionsClient:
    """Instantiate and return account-connections client"""

    return AccountConnectionsClient(
        client_session=client_session, base_url=settings.account_connections_base_url
    )
