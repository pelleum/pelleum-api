from typing import Optional

from pydantic import BaseModel, Field, constr


class CreatePaymentIntentRequest(BaseModel):
    currency: str = Field(
        ...,
        description='The currency for the payment intent',
        example='usd'
    )
    amount: int = Field(
        ...,
        description='The amount of the payment intent',
        example=1
    )

class CreatePaymentIntentResponse(BaseModel):
    clientSecret: Optional[str] = Field(
        None,
        description='The client secret which is returned when the paymentIntent is created',
        example="pi_1DpzYU2eZvKYlo2Cl8AsYeyF_secret_1xu1AlPEQqRRbZ1Ca74h9L1Zo"
    )

class WebhookRequest(BaseModel):
    pass

class WebhookResponse(BaseModel):
    pass

# class CustomerRequest(BaseModel):
#     pass

# class CustomerResponse(BaseModel):
#     pass

class SubscriptionRequest(BaseModel):
    userId: int = Field(
        ...,
        description='The user_id of the current logged in user',
        example='1'
    )
    priceId: str = Field(
        ...,
        description='The price_id of the selected subscription',
        example='price_1KXWJqLn3LY7wE9KXna1IPLV'
    )
    subscriptionId: Optional[str] = Field(
        None,
        description='The subscription_id for the subscription you want to modify',
        example='sub_JgRjFjhKbtD2qz'
    )

class SubscriptionResponse(BaseModel):
    subscriptionId: Optional[str] = Field(
        None,
        description='The subscription_id of the created subscription',
        example='sub_JgRjFjhKbtD2qz'
    )
    clienSecret: Optional[str] = Field(
        None,
        description='The client secret for the paymentIntent of the latest invoice for the subscription',
        example=''
    )


