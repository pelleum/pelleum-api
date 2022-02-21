from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm

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
from app.usecases.interfaces.user_repo import IUserRepo
from app.usecases.schemas import auth, users

auth_router = APIRouter(tags=["Users"])


@auth_router.post("/login", response_model=users.UserWithAuthTokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users_repo: IUserRepo = Depends(get_users_repo),
) -> users.UserWithAuthTokenResponse:

    user = await users_repo.retrieve_user_with_filter(username=form_data.username)

    if not user:
        raise pelleum_errors.login_error

    password_matches = await verify_password(user=user, password=form_data.password)

    if not password_matches:
        raise pelleum_errors.login_error

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
    users_repo: IUserRepo = Depends(get_users_repo),
    portfolio_repo: IPortfolioRepo = Depends(get_portfolio_repo),
) -> users.UserWithAuthTokenResponse:
    """Upon signup, validates inputs, creates new user object, and creates new portfolio object."""

    # 1. Validate inputs
    await validate_password(password=body.password)
    await validate_email(email=body.email)

    password_context = await get_password_context()

    email_already_exists = await users_repo.retrieve_user_with_filter(email=body.email)
    if email_already_exists:
        raise await pelleum_errors.PelleumErrors(
            detail="An account with this email already exists. Please choose another email."
        ).account_exists()

    username_already_exists = await users_repo.retrieve_user_with_filter(
        username=body.username
    )
    if username_already_exists:
        raise await pelleum_errors.PelleumErrors(
            detail="An account with this username already exists. Please choose another username."
        ).account_exists()

    # 2. Create new user object
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
    response_model=users.UserResponse,
)
async def update_user(
    body: users.UserCreate = Body(...),
    users_repo: IUserRepo = Depends(get_users_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> users.UserResponse:

    password_context = await get_password_context()
    updated_user = await users_repo.update(
        updated_user=body,
        user_id=authorized_user.user_id,
        password_context=password_context,
    )
    updated_user_raw = updated_user.dict()

    return users.UserResponse(**updated_user_raw)


@auth_router.get("", response_model=users.UserResponse)
async def get_current_user(
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> users.UserResponse:
    return users.UserResponse(**authorized_user.dict())
