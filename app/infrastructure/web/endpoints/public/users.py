from turtle import update
from typing import Union

from fastapi import APIRouter, Body, Depends, Path
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import conint

from app.dependencies import (
    create_access_token,
    get_current_active_user,
    get_password_context,
    get_portfolio_repo,
    get_users_repo,
    validate_email,
    validate_password,
    verify_password,
)
from app.libraries import pelleum_errors
from app.usecases.interfaces.portfolio_repo import IPortfolioRepo
from app.usecases.interfaces.user_repo import IUsersRepo
from app.usecases.schemas import auth, users

auth_router = APIRouter(tags=["Users"])


@auth_router.post("/login", response_model=users.UserWithAuthTokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users_repo: IUsersRepo = Depends(get_users_repo),
) -> users.UserWithAuthTokenResponse:

    user = await users_repo.retrieve_user_with_filter(username=form_data.username)

    if not user:
        raise await pelleum_errors.PelleumErrors(
            detail="Incorrect username or password."
        ).invalid_credentials()

    password_matches = await verify_password(user=user, password=form_data.password)

    if not password_matches:
        raise await pelleum_errors.PelleumErrors(
            detail="Incorrect username or password."
        ).invalid_credentials()

    access_token = await create_access_token(
        data=auth.AuthDataToCreateToken(sub=user.username)
    )

    return users.UserWithAuthTokenResponse(
        **user.dict(), access_token=access_token, token_type="bearer"
    )


@auth_router.post(
    "",
    status_code=201,
    response_model=users.UserWithAuthTokenResponse,
)
async def create_new_user(
    body: users.UserCreate = Body(...),
    users_repo: IUsersRepo = Depends(get_users_repo),
    portfolio_repo: IPortfolioRepo = Depends(get_portfolio_repo),
) -> users.UserWithAuthTokenResponse:
    """Upon signup, validates inputs, creates new user object, and creates new portfolio object."""

    # 1. Validate inputs
    await validate_inputs(users_repo=users_repo, data=body)

    # 2. Create new user object
    password_context = await get_password_context()
    new_user = await users_repo.create(new_user=body, password_context=password_context)
    new_user_raw = new_user.dict()

    access_token = await create_access_token(
        data=auth.AuthDataToCreateToken(sub=body.username)
    )

    return users.UserWithAuthTokenResponse(
        **new_user_raw, access_token=access_token, token_type="bearer"
    )


@auth_router.patch(
    "",
    status_code=200,
    response_model=users.UserWithAuthTokenResponse,
)
async def update_user(
    body: users.UserUpdate = Body(...),
    users_repo: IUsersRepo = Depends(get_users_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> users.UserWithAuthTokenResponse:
    """Update a user object's attributes."""

    # 1. Validate inputes
    await validate_inputs(users_repo=users_repo, data=body)

    # 2. Update user
    password_context = await get_password_context()
    updated_user = await users_repo.update(
        updated_user=body,
        user_id=authorized_user.user_id,
        password_context=password_context,
    )
    updated_user_raw = updated_user.dict()

    access_token = await create_access_token(
        data=auth.AuthDataToCreateToken(sub=updated_user.username)
    )

    return users.UserWithAuthTokenResponse(
        **updated_user_raw, access_token=access_token, token_type="bearer"
    )


@auth_router.get("", response_model=users.UserResponse)
async def get_current_user(
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> users.UserResponse:
    return users.UserResponse(**authorized_user.dict())


async def validate_inputs(
    users_repo: IUsersRepo, data=Union[users.UserCreate, users.UserUpdate]
) -> None:
    """Validate data inputes at user creation and update"""

    if data.password:
        await validate_password(password=data.password)

    if data.email:
        await validate_email(email=data.email)
        email_already_exists = await users_repo.retrieve_user_with_filter(
            email=data.email
        )
        if email_already_exists:
            raise await pelleum_errors.PelleumErrors(
                detail="An account with this email already exists. Please choose another email."
            ).account_exists()

    if data.username:
        username_already_exists = await users_repo.retrieve_user_with_filter(
            username=data.username
        )
        if username_already_exists:
            raise await pelleum_errors.PelleumErrors(
                detail="An account with this username already exists. Please choose another username."
            ).account_exists()


@auth_router.patch("/block/{blocked_user_id}", status_code=201)
async def block_user(
    blocked_user_id: conint(gt=0, lt=100000000000) = Path(...),
    users_repo: IUsersRepo = Depends(get_users_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:
    """Block a user."""

    # 1. See if user is already blocked
    user_object = await users_repo.retrieve_user_with_filter(
        user_id=authorized_user.user_id
    )

    if user_object.block_list:
        if blocked_user_id in user_object.block_list:
            raise await pelleum_errors.PelleumErrors(
                detail="This user has already been blocked."
            ).unique_constraint()

        user_object.block_list.append(blocked_user_id)
    else:
        user_object.block_list = [blocked_user_id]
    
    await users_repo.manage_blocks(
        user_id=authorized_user.user_id, updated_block_list=user_object.block_list
    )


@auth_router.delete("/block/{blocked_user_id}", status_code=200)
async def unblock_user(
    blocked_user_id: conint(gt=0, lt=100000000000) = Path(...),
    users_repo: IUsersRepo = Depends(get_users_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> None:
    """Un-block a user."""

    # 1. See if user is already blocked
    user_object = await users_repo.retrieve_user_with_filter(
        user_id=authorized_user.user_id
    )

    if not user_object.block_list:
        raise await pelleum_errors.PelleumErrors(
            detail="This user is not blocked, so you can't remove a block."
        ).general_error()

    if blocked_user_id not in user_object.block_list:
        raise await pelleum_errors.PelleumErrors(
            detail="This user is not blocked, so you can't remove a block."
        ).general_error()

    # 2. Remove user_id from user's block list
    user_object.block_list.remove(blocked_user_id)
    await users_repo.manage_blocks(
        user_id=authorized_user.user_id, updated_block_list=user_object.block_list
    )
