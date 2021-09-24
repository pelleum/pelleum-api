from fastapi import HTTPException, status


login_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

invalid_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

inactive_user_error = HTTPException(status_code=400, detail="Inactive user")

email_already_exists = HTTPException(
    status_code=403,
    detail="An account with this email already exists. Please choose another email.",
)
username_already_exists = HTTPException(
    status_code=403,
    detail="An account with this username already exists. Please choose another username.",
)
