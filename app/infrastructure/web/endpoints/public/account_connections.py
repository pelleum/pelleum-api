from fastapi import APIRouter, Body, Depends, Path, Request, Response
from pydantic import constr

from app.dependencies import get_account_connections_client, get_current_active_user
from app.usecases.interfaces.clients.account_connections import (
    IAccountConnectionsClient,
)
from app.usecases.schemas import account_connections, users

institution_router = APIRouter(tags=["Institutions"])


@institution_router.get(
    "",
)
async def get_all_supported_institutions(
    response: Response,
    request: Request,
    account_connections_client: IAccountConnectionsClient = Depends(
        get_account_connections_client
    ),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
):
    """Retrieve all Pelleum supported institutions (pass through)"""

    user_json_web_token = request.headers.get("Authorization")

    account_connections_response = await account_connections_client.get_institutions(
        user_auth=user_json_web_token
    )

    response.status_code = account_connections_response.status
    return account_connections_response.body


@institution_router.get(
    "/connections",
)
async def retrieve_institution_connections(
    response: Response,
    request: Request,
    account_connections_client: IAccountConnectionsClient = Depends(
        get_account_connections_client
    ),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
):
    """Retrieve a user's connected accounts (pass through)"""

    user_json_web_token = request.headers.get("Authorization")

    account_connections_response = (
        await account_connections_client.get_account_connections(
            user_auth=user_json_web_token
        )
    )

    response.status_code = account_connections_response.status
    return account_connections_response.body


@institution_router.delete(
    "/{institution_id}",
)
async def delete_institution_connection(
    response: Response,
    request: Request,
    institution_id: constr(max_length=100) = Path(...),
    account_connections_client: IAccountConnectionsClient = Depends(
        get_account_connections_client
    ),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
):
    """Deactivate a user's connected account (pass through)"""

    user_json_web_token = request.headers.get("Authorization")

    account_connections_response = await account_connections_client.delete_connection(
        institution_id=institution_id, user_auth=user_json_web_token
    )

    response.status_code = account_connections_response.status
    return account_connections_response.body


@institution_router.post(
    "/login/{institution_id}",
)
async def login_to_institution(
    response: Response,
    request: Request,
    institution_id: constr(max_length=100) = Path(...),
    body: account_connections.LoginRequest = Body(...),
    account_connections_client: IAccountConnectionsClient = Depends(
        get_account_connections_client
    ),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
):
    """Login to institution (pass through)"""

    user_json_web_token = request.headers.get("Authorization")

    account_connections_response = await account_connections_client.login(
        payload=body.dict(),
        institution_id=institution_id,
        user_auth=user_json_web_token,
    )

    response.status_code = account_connections_response.status
    return account_connections_response.body


@institution_router.post(
    "/login/{institution_id}/verify",
)
async def verify_login_with_code(
    response: Response,
    request: Request,
    institution_id: constr(max_length=100) = Path(...),
    body: account_connections.MultiFactorAuthCodeRequest = Body(...),
    account_connections_client: IAccountConnectionsClient = Depends(
        get_account_connections_client
    ),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
):
    """Verify login to institution with verifaction code (pass through)"""

    user_json_web_token = request.headers.get("Authorization")

    account_connections_response = await account_connections_client.verify_mfa_code(
        payload=body.dict(),
        institution_id=institution_id,
        user_auth=user_json_web_token,
    )

    response.status_code = account_connections_response.status
    return account_connections_response.body
