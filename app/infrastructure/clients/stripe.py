from typing import Any

import stripe

from app.libraries.pelleum_errors import PelleumErrors
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
        try:
            customer = stripe.Customer.create(email=email)
        except stripe.error.StripeError as e:
            raise await PelleumErrors(detail=str(e)).stripe_client_error()
        return subscriptions.StripeCustomer(id=customer.id)

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_behavior: str,
    ) -> subscriptions.StripeSubscription:
        try:
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
        except stripe.error.StripeError as e:
            raise await PelleumErrors(detail=str(e)).stripe_client_error()
        return subscriptions.StripeSubscription(
            id=subscription.id,
            client_secret=subscription.latest_invoice.payment_intent.client_secret,
        )

    async def delete_subscription(
        self,
        stripe_subscription_id: str,
    ) -> subscriptions.StripeSubscription:
        try:
            deletedSubscription = stripe.Subscription.delete(stripe_subscription_id)
        except stripe.error.StripeError as e:
            raise await PelleumErrors(detail=str(e)).stripe_client_error()
        return subscriptions.StripeSubscription(id=deletedSubscription.id)

    async def construct_webhook_event(
        self,
        payload: Any,
        sig_header: str,
    ) -> subscriptions.WebhookEvent:
        try:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=sig_header, secret=self.__webhook_secret
            )
        except stripe.error.StripeError as e:
            raise await PelleumErrors(detail=str(e)).stripe_client_error()
        return subscriptions.WebhookEvent(data=event["data"], event_type=event["type"])

    async def retrieve_payment_intent(
        self,
        payment_intent_id: str,
    ) -> subscriptions.StripePaymentIntent:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            raise await PelleumErrors(detail=str(e)).stripe_client_error()
        return subscriptions.StripePaymentIntent(
            payment_method=payment_intent.payment_method
        )

    async def modify_subscription(
        self, stripe_subscription_id: str, default_payment_method: str
    ) -> subscriptions.StripeSubscription:
        try:
            subscription = stripe.Subscription.modify(
                stripe_subscription_id, default_payment_method=default_payment_method
            )
        except stripe.error.StripeError as e:
            raise await PelleumErrors(detail=str(e)).stripe_client_error()
        return subscriptions.StripeSubscription(id=subscription.id)
