from fastapi import APIRouter, Depends, HTTPException, status, Body
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordRequestForm


# clean up the above ^

from app.usecases.services.user_manager import UserManager
from app.dependencies import get_user_manager_service, get_oauth2_scheme
from app.usecases.schemas import auth
from app.usecases.schemas import users



auth_router = APIRouter(tags=["auth"])




# async def get_current_user(token: str = Depends(get_oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user


# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


@auth_router.post("/token", response_model=auth.JWTResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_manager_service: UserManager = Depends(get_user_manager_service),
) -> auth.JWTResponse:
    user = await user_manager_service.authenticate_user(
        user_name=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token: str = await user_manager_service.create_access_token(
        data=auth.AuthDataToCreateToken(sub=user.username)
    )

    return auth.JWTResponse(access_token=access_token, token_type="bearer")



@auth_router.post(
    "/create_user",
    status_code=201,
    response_model=users.UserCreateResponse,
)
async def create_new_user(
    body: users.UserCreate = Body(...),
    user_manager_service: UserManager = Depends(get_user_manager_service),
) -> users.UserCreateResponse:

    new_user = await user_manager_service.create_new_user(user=body)

    return users.UserCreateResponse(
        email=new_user.email,
        username=new_user.username,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
    )


# @auth_router.get("/users/me", response_model=User)
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user