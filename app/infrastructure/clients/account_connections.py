from typing import Any, Mapping, Optional

import aiohttp

from app.usecases.interfaces.clients.account_connections import (
    IAccountConnectionsClient,
)
from app.usecases.schemas import account_connections


class AccountConnectionsClient(IAccountConnectionsClient):
    """Faciliates communication with account-connections API"""

    def __init__(self, client_session: aiohttp.client.ClientSession, base_url: str):
        self.client_session = client_session
        self.base_url = base_url

    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Mapping[str, str]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> account_connections.AccountConnectionsResponse:
        """Make API call"""

        async with self.client_session.request(
            method,
            self.base_url + endpoint,
            headers=headers,
            json=json_body,
            verify_ssl=False,
        ) as response:
            try:
                response_json = await response.json()
            except Exception:
                response_text = await response.text()
                raise account_connections.AccountConnectionsException(  # pylint: disable=raise-missing-from
                    f"Account Connections Client Error: Response status: {response.status}, Response Text: {response_text}"
                )

            return account_connections.AccountConnectionsResponse(
                body=response_json, status=response.status
            )

    async def get_institutions(
        self, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends request to get all supported brokerages to account-connections API"""

        return await self.api_call(
            method="GET", endpoint="", headers={"Authorization": user_auth}
        )

    async def get_account_connections(
        self, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends request to get all account connections to account-connections API"""

        return await self.api_call(
            method="GET", endpoint="/connections", headers={"Authorization": user_auth}
        )

    async def delete_connection(
        self, institution_id: str, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends request to delete institution connection to account-connections API"""

        return await self.api_call(
            method="DELETE",
            endpoint=f"/{institution_id}",
            headers={"Authorization": user_auth},
        )

    async def login(
        self, payload: Mapping[str, str], institution_id: str, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends brokerage linking information to account-connections API"""

        return await self.api_call(
            method="POST",
            endpoint=f"/login/{institution_id}",
            json_body=payload,
            headers={"Authorization": user_auth},
        )

    async def verify_mfa_code(
        self, payload: Mapping[str, Any], institution_id: str, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends verification code request to account-connections API"""

        return await self.api_call(
            method="POST",
            endpoint=f"/login/{institution_id}/verify",
            json_body=payload,
            headers={"Authorization": user_auth},
        )
