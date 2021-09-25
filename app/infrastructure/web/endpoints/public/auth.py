from passlib.context import CryptContext
from app.usecases.schemas.database import UserInDB
from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import (
    get_users_repo,
    get_password_context,
    verify_password,
    create_access_token,
    get_current_active_user,
    validate_password,
    validate_email,
)
from app.libraries import pelleum_errors
from app.usecases.schemas import auth
from app.usecases.schemas import users
from app.infrastructure.db.repos.user_repo import UsersRepo


auth_router = APIRouter(tags=["auth"])


@auth_router.post("/token", response_model=auth.JWTResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users_repo: UsersRepo = Depends(get_users_repo),
) -> auth.JWTResponse:

    user: UserInDB = await users_repo.retrieve_user_with_filter(
        username=form_data.username
    )

    if not user:
        raise pelleum_errors.login_error

    password_matches = await verify_password(user=user, password=form_data.password)

    if not password_matches:
        raise pelleum_errors.login_error

    access_token: str = await create_access_token(
        data=auth.AuthDataToCreateToken(sub=user.username)
    )

    return auth.JWTResponse(access_token=access_token, token_type="bearer")


@auth_router.post(
    "/users/create",
    status_code=201,
    response_model=users.UserResponse,
)
async def create_new_user(
    body: users.UserCreate = Body(...), users_repo: UsersRepo = Depends(get_users_repo)
) -> users.UserResponse:

    await validate_password(password=body.password)
    await validate_email(email=body.email)

    password_context: CryptContext = await get_password_context()

    email_already_exists: UserInDB = await users_repo.retrieve_user_with_filter(
        email=body.email
    )
    if email_already_exists:
        raise await pelleum_errors.AccountAlreadyExists(
            detail="An account with this email already exists. Please choose another email."
        ).account_exists()

    username_already_exists: UserInDB = await users_repo.retrieve_user_with_filter(
        username=body.username
    )
    if username_already_exists:
        raise await pelleum_errors.AccountAlreadyExists(
            detail="An account with this username already exists. Please choose another username."
        ).account_exists()

    new_user: UserInDB = await users_repo.create(
        new_user=body, password_context=password_context
    )
    new_user_raw = new_user.dict()

    return users.UserResponse(**new_user_raw)


@auth_router.patch(
    "/users/update",
    status_code=200,
    response_model=users.UserResponse,
)
async def update_user(
    body: users.UserCreate = Body(...), users_repo: UsersRepo = Depends(get_users_repo)
) -> users.UserResponse:

    password_context: CryptContext = await get_password_context()
    updated_user: UserInDB = await users_repo.update(
        updated_user=body, password_context=password_context
    )
    updated_user_raw = updated_user.dict()

    return users.UserResponse(**updated_user_raw)


@auth_router.get("/users/me", response_model=users.UserResponse)
async def read_users_me(
    current_user: users.UserResponse = Depends(get_current_active_user),
):
    return users.UserResponse(**current_user.dict())
