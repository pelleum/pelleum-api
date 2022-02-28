from app.infrastructure.clients.stripe import StripeClient
from app.settings import settings
from app.usecases.interfaces.clients.stripe import IStripeClient


async def get_stripe_client(
) -> IStripeClient:
    """Instantiate and return stripe client"""

    return StripeClient(
        api_key=settings.stripe_secret_key, webhook_secret=settings.stripe_webhook_secret 
    )