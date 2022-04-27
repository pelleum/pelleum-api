from fastapi import HTTPException, status


class PelleumErrors:
    def __init__(self, detail: str = None):
        self.detail = detail

    async def invalid_credentials(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.detail if self.detail else "Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def inactive_user(self):
        return HTTPException(status_code=400, detail="Inactive user")

    async def account_exists(self):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=self.detail
            if self.detail
            else "An account with this username or email already exists.",
        )

    async def invalid_password(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail if self.detail else "The submitted password is invalid.",
        )

    async def invalid_email(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail if self.detail else "The submitted email is invalid.",
        )

    async def invalid_resource_id(self):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=self.detail
            if self.detail
            else "The supplied resource ID is invalid.",
        )

    async def unique_constraint(self):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=self.detail if self.detail else "This resource already exists.",
        )

    async def client_error(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail if self.detail else "There was an client error.",
        )

    async def general_error(self):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=self.detail
            if self.detail
            else "There was an internal server error.",
        )

    async def account_connection_error(self):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=self.detail
            if self.detail
            else "There was an external account connection error.",
        )

    async def invalid_query_params(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail
            if self.detail
            else "Invalid query parameters sent to the endpiont.",
        )

    async def access_forbidden(self):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=self.detail
            if self.detail
            else "Access to this resource is forbidden.",
        )

    async def array_too_long(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The maximum amount of supporting sources is 10.",
        )

    async def stripe_client_error(self):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=self.detail if self.detail else "There was an external Stripe error",
        )
