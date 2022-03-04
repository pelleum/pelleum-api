from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SubscriptionTier(str, Enum):
    PRO = "PRO"


class WebhookEvent(BaseModel):
    data: dict
    event_type: str


class CreateSubscription(BaseModel):
    subscription_tier: SubscriptionTier = Field(
        ...,
        description="The subscription tier for the subscription being created",
        example="PRO",
    )
    price_id: str = Field(
        ...,
        description="The stripe price_id of the selected subscription",
        example="price_1KXWJqLn3LY7wE9KXna1IPLV",
    )


class CancelSubscription(BaseModel):
    stripe_subscription_id: str = Field(
        ...,
        description="The stripe subscription_id for the subscription you want to cancel",
        example="sub_JgRjFjhKbtD2qz",
    )


class SubscriptionRepoCreate(BaseModel):
    user_id: int
    subscription_tier: SubscriptionTier
    stripe_customer_id: str
    stripe_subscription_id: str
    is_active: bool


class SubscriptionInDB(SubscriptionRepoCreate):
    """Database Model"""

    subscription_id: int
    created_at: datetime
    updated_at: datetime


class SubscriptionRepoUpdate(BaseModel):
    subscription_id: Optional[int] = None
    user_id: Optional[int] = None
    subscription_tier: Optional[SubscriptionTier] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    is_active: Optional[bool] = None


class StripeCustomer(BaseModel):
    id: str = Field(
        ...,
        description="The customer_id for the stripe customer",
        example="cus_LE7Hrfouov20uY",
    )


class StripeSubscription(BaseModel):
    id: str = Field(
        ...,
        description="The stripe subscription_id for the subscription",
        example="sub_JgRjFjhKbtD2qz",
    )
    client_secret: Optional[str] = Field(
        None,
        description="The stripe client secret for the payment intent",
        example="src_client_secret_5WeaNxZyiWkyUnNbZr2ESD0n",
    )


class StripePaymentIntent(BaseModel):
    payment_method: str = Field(
        ...,
        description="The payment method for the stripe payment intent",
        example="pm_1KXf3PLn3LY7wE9K53i97hrx",
    )
