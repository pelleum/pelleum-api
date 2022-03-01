from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WebhookEvent(BaseModel):
    data: dict
    event_type: str


class CreateSubscription(BaseModel):
    subscription_tier: str = Field(
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


class SubscriptionInDB(BaseModel):
    """Database Model"""

    subscription_id: int
    user_id: int
    subscription_tier: str
    stripe_customer_id: str
    stripe_subscription_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


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
