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
