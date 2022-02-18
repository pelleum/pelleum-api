from typing import Any, Mapping, Optional

from pydantic import BaseModel, Field, constr


class LoginRequest(BaseModel):
    """JSON body model of request"""

    username: constr(max_length=100) = Field(
        ...,
        description="An encrypted, optional username for the linked account.",
        example="myusername",
    )
    password: constr(max_length=100) = Field(
        ...,
        description="An encrypted, optional password for the linked account.",
        example="password",
    )


class MultiFactorAuthCodeRequest(BaseModel):
    """JSON body model of MFA verify request"""

    sms_code: Optional[constr(max_length=10)] = Field(
        None,
        description="The multifactor (sms) authentication code sent to the user's phone.",
        example="149837",
    )
    challenge_id: Optional[constr(max_length=100)] = Field(
        None,
        description="The unique identifier for the challenge that Robinhood issues to those who have 2FA disabled on their accounts.",
        example="ca3cf668-404c-49d2-8510-ea9948ff66aa",
    )


class AccountConnectionsException(Exception):
    """Generic account-connections API exception"""


class AccountConnectionsResponse(BaseModel):
    """Repsonse from account-connetions API"""

    body: Optional[Mapping[str, Any]]
    status: int
