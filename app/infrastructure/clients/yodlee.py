import aiohttp
import os
from dotenv import load_dotenv
from app.usecases.interfaces.yodlee_interface import (
    IYodleeClient,
    YodleeException,
)
from typing import Mapping, Any
from app.settings import settings

load_dotenv()


class YodleeClient(IYodleeClient):
    def __init__(self, client_session, base_url, bearer_token=None):
        self.client_session = client_session
        self.base_url = base_url
        self.bearer_token = bearer_token

    async def get_header(self, token_update_required=False, user_login_name=None):
        if token_update_required and user_login_name is not None:
            return {"Api-version": "1.1", "loginName": user_login_name}
        auth_header = "Bearer " + self.bearer_token
        return {"Api-version": "1.1", "Authorization": auth_header}

    async def api_call(
        self,
        method: str,
        headers: dict,
        endpoint: str,
        json_body: Any = None,
        data: Any = None,
    ) -> Mapping[str, Any]:
        async with self.client_session.request(
            method,
            self.base_url + endpoint,
            headers=headers,
            data=data,
            json=json_body,
        ) as response:
            try:
                resp_json = await response.json()
            except Exception:
                resp_json = response
            if response.status >= 300:
                raise YodleeException(
                    f"Yodlee Client Error: {response.status} - {resp_json}"
                )
            return resp_json

    async def get_accounts(self):
        headers = await self.get_header()

        return await self.api_call(
            method="GET",
            endpoint="/accounts",
            headers=headers,
        )

    async def get_transactions(self):
        headers = await self.get_header()

        return await self.api_call(
            method="GET",
            endpoint="/transactions",
            headers=headers,
        )

    async def get_bearer_token(self):
        headers = await self.get_header(
            token_update_required=True,
            user_login_name=settings.user_login_name,
        )
        data_body = {
            "clientId": settings.yodlee_client_id,
            "secret": settings.yodlee_secret,
        }
        # data_body = aiohttp.FormData(data_body)
        response = await self.api_call(
            method="POST",
            endpoint="/auth/token",
            headers=headers,
            data=data_body,
        )
        access_token = response["token"]["accessToken"]
        self.bearer_token = access_token
        print("\nBearer token updated.\n")
