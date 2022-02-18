from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from app.usecases.schemas import account_connections


class IAccountConnectionsClient(ABC):
    @abstractmethod
    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Mapping[str, str]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> account_connections.AccountConnectionsResponse:
        """Make API call"""

    @abstractmethod
    async def get_institutions(
        self, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends request to get all supported brokerages to account-connections API"""

    @abstractmethod
    async def get_account_connections(
        self, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends request to get all account connections to account-connections API"""

    @abstractmethod
    async def delete_connection(
        self, institution_id: str, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends request to delete institution connection to account-connections API"""

    @abstractmethod
    async def login(
        self, payload: Mapping[str, str], institution_id: str, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends brokerage linking information to account-connections API"""

    @abstractmethod
    async def verify_mfa_code(
        self, payload: Mapping[str, Any], institution_id: str, user_auth: str
    ) -> account_connections.AccountConnectionsResponse:
        """Sends verification code request to account-connections API"""
