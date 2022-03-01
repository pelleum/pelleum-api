from typing import Any

import stripe

from app.usecases.interfaces.clients.stripe import IStripeClient
from app.usecases.schemas import subscriptions


class StripeClient(IStripeClient):
    def __init__(self, api_key, webhook_secret) -> None:
        stripe.api_key = api_key
        self.__webhook_secret = webhook_secret

    async def create_customer(
        self,
        email: str,
    ) -> subscriptions.StripeCustomer:
        customer = stripe.Customer.create(email=email)
        return subscriptions.StripeCustomer(id=customer.id)

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_behavior: str,
    ) -> subscriptions.StripeSubscription:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[
                {
                    "price": price_id,
                }
            ],
            payment_behavior=payment_behavior,
            expand=["latest_invoice.payment_intent"],
        )
        return subscriptions.StripeSubscription(
            id=subscription.id,
            client_secret=subscription.latest_invoice.payment_intent.client_secret,
        )

    async def delete_subscription(
        self,
        stripe_subscription_id: str,
    ) -> subscriptions.StripeSubscription:
        deletedSubscription = stripe.Subscription.delete(stripe_subscription_id)
        return subscriptions.StripeSubscription(id=deletedSubscription.id)

    async def construct_webhook_event(
        self,
        payload: Any,
        sig_header: str,
    ) -> subscriptions.WebhookEvent:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=self.__webhook_secret
        )
        return subscriptions.WebhookEvent(data=event["data"], event_type=event["type"])

    async def retrieve_payment_intent(
        self,
        payment_intent_id: str,
    ) -> subscriptions.StripePaymentIntent:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return subscriptions.StripePaymentIntent(
            payment_method=payment_intent.payment_method
        )

    async def modify_subscription(
        self, stripe_subscription_id: str, default_payment_method: str
    ) -> subscriptions.StripeSubscription:
        subscription = stripe.Subscription.modify(
            stripe_subscription_id, default_payment_method=default_payment_method
        )
        return subscriptions.StripeSubscription(id=subscription.id)
