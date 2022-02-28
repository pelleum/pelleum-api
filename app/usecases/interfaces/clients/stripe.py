from abc import ABC, abstractmethod

from app.usecases.schemas import subscriptions


class IStripeClient(ABC):
    @abstractmethod
    async def create_customer(
        self,
        email: str,
    ) -> subscriptions.StripeCustomer:
        """Creates a customer"""

    @abstractmethod
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_behaviour: str,
    ) -> subscriptions.StripeSubscription:
        """Creates a subscription"""

    @abstractmethod
    async def delete_subscription(
        self,
        subscription_id: str,
    ) -> subscriptions.StripeSubscription:
        """Deletes a subscription"""

    @abstractmethod
    async def construct_webhook_event(
        self,
        payload: dict,
        sig_header: str,
        secret: str
    ) -> subscriptions.WebhookEvent:
        """Constructs a webhook event"""

    @abstractmethod
    async def retrieve_payment_intent(
        self,
        payment_intent_id: str,
    ) -> subscriptions.StripePaymentIntent:
        """Retrieves a payment intent from stripe"""

    @abstractmethod
    async def modify_subscription(
        self,
        stripe_subscription_id: str,
        default_payment_method: str
    ) -> subscriptions.StripeSubscription:
        """Modify a stripe subscription"""
