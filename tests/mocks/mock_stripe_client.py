from typing import Any

from app.usecases.interfaces.clients.stripe import IStripeClient
from app.usecases.schemas import subscriptions


class MockStripeClient(IStripeClient):
    async def create_customer(
        self,
        email: str,
    ) -> subscriptions.StripeCustomer:
        return subscriptions.StripeCustomer(id="cus_123")

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_behavior: str,
    ) -> subscriptions.StripeSubscription:
        return subscriptions.StripeSubscription(
            id="sub_123",
            client_secret="src_123",
        )

    async def delete_subscription(
        self,
        stripe_subscription_id: str,
    ) -> subscriptions.StripeSubscription:
        return subscriptions.StripeSubscription(id="sub_123")

    async def construct_webhook_event(
        self,
        payload: Any,
        sig_header: str,
    ) -> subscriptions.WebhookEvent:
        return subscriptions.WebhookEvent(
            data={
                "object": {
                    "billing_reason": "subscription_create",
                    "subscription": "sub_123",
                    "payment_intent": "pi_123",
                }
            },
            event_type="invoice.payment_succeeded",
        )

    async def retrieve_payment_intent(
        self,
        payment_intent_id: str,
    ) -> subscriptions.StripePaymentIntent:
        return subscriptions.StripePaymentIntent(payment_method="pm_123")

    async def modify_subscription(
        self, stripe_subscription_id: str, default_payment_method: str
    ) -> subscriptions.StripeSubscription:
        return subscriptions.StripeSubscription(id="sub_123")
