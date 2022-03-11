from fastapi import APIRouter, Body, Depends, Path, Request, Response

from app.dependencies.auth import get_current_active_user
from app.dependencies.repos import get_subscriptions_repo
from app.dependencies.stripe import get_stripe_client
from app.usecases.interfaces.clients.stripe import IStripeClient
from app.usecases.interfaces.subscriptions_repo import ISubscriptionsRepo
from app.usecases.schemas import subscriptions, users

subscriptions_router = APIRouter(tags=["Subscriptions"])


@subscriptions_router.post(
    "/create", status_code=201, response_model=subscriptions.StripeSubscription
)
async def create_subscription(
    body: subscriptions.CreateSubscription = Body(...),
    stripe_client: IStripeClient = Depends(get_stripe_client),
    subscriptions_repo: ISubscriptionsRepo = Depends(get_subscriptions_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> subscriptions.StripeSubscription:
    """Creates a new Stripe subscription. Also adds/updates a record to the subscription db table."""
    user_id = authorized_user.user_id
    subscription_tier = body.subscription_tier
    existing_customer = await subscriptions_repo.retrieve_subscription_with_filter(
        user_id=user_id,
    )
    existing_subscription = await subscriptions_repo.retrieve_subscription_with_filter(
        user_id=user_id, subscription_tier=subscription_tier
    )
    if existing_customer:
        customer_id = existing_customer.stripe_customer_id
    else:
        customer = await stripe_client.create_customer(email=authorized_user.email)
        customer_id = customer.id

    created_stripe_subscription = await stripe_client.create_subscription(
        customer_id=customer_id,
        price_id=body.price_id,
        payment_behavior="default_incomplete",
    )

    if existing_subscription:
        updated_record = subscriptions.SubscriptionRepoUpdate(
            subscription_id=existing_subscription.subscription_id,
            stripe_subscription_id=created_stripe_subscription.id,
            is_active=False,  # wait until webhook is received to set this to True
        )
        await subscriptions_repo.update(updated_subscription=updated_record)
    else:
        new_record = subscriptions.SubscriptionRepoCreate(
            user_id=user_id,
            subscription_tier=subscription_tier,
            stripe_customer_id=customer_id,
            stripe_subscription_id=created_stripe_subscription.id,
            is_active=False,  # wait until webhook is received to set this to True
        )
        await subscriptions_repo.create(new_subscription=new_record)

    return created_stripe_subscription


@subscriptions_router.post(
    "/cancel",
    status_code=201,
    response_model=subscriptions.StripeSubscription,
)
async def cancel_subscription(
    body: subscriptions.CancelSubscription = Body(...),
    stripe_client: IStripeClient = Depends(get_stripe_client),
    subscriptions_repo: ISubscriptionsRepo = Depends(get_subscriptions_repo),
) -> subscriptions.StripeSubscription:
    """Cancels a Stripe subscription. Updates the subscription db record's is_active
    flag to false"""
    stripe_subscription = await stripe_client.delete_subscription(
        body.stripe_subscription_id
    )

    updated_record = subscriptions.SubscriptionRepoUpdate(
        stripe_subscription_id=stripe_subscription.id, is_active=False
    )

    await subscriptions_repo.update(updated_subscription=updated_record)

    return stripe_subscription


@subscriptions_router.get(
    "/{subscription_tier}",
    status_code=200,
    response_model=subscriptions.SubscriptionInDB,
)
async def get_subscription(
    subscription_tier: str = Path(...),
    subscriptions_repo: ISubscriptionsRepo = Depends(get_subscriptions_repo),
    authorized_user: users.UserInDB = Depends(get_current_active_user),
) -> subscriptions.SubscriptionInDB:
    """This endpoint returns the subscription record for the current logged in user
    and the provided subscription tier"""
    return await subscriptions_repo.retrieve_subscription_with_filter(
        user_id=authorized_user.user_id, subscription_tier=subscription_tier
    )


@subscriptions_router.post(
    "/webhook_received",
)
async def webhook_received(
    request: Request,
    response: Response,
    stripe_client: IStripeClient = Depends(get_stripe_client),
    subscriptions_repo: ISubscriptionsRepo = Depends(get_subscriptions_repo),
) -> Response:
    """Listens for webhook calls from Stripe"""

    # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
    signature = request.headers.get("stripe-signature")
    payload = await request.body()
    event = await stripe_client.construct_webhook_event(
        payload=payload,
        sig_header=signature,
    )

    data = event.data
    event_type = event.event_type
    data_object = data["object"]

    if event_type == "invoice.paid":
        if stripe_subscription_id := data_object["subscription"]:
            updated_record = subscriptions.SubscriptionRepoUpdate(
                stripe_subscription_id=stripe_subscription_id, is_active=True
            )
            await subscriptions_repo.update(updated_subscription=updated_record)
    elif event_type == "invoice.payment_failed":
        if stripe_subscription_id := data_object["subscription"]:
            updated_record = subscriptions.SubscriptionRepoUpdate(
                stripe_subscription_id=stripe_subscription_id, is_active=False
            )
            await subscriptions_repo.update(updated_subscription=updated_record)
    elif event_type == "invoice.payment_succeeded":
        if data_object["billing_reason"] == "subscription_create":
            stripe_subscription_id = data_object["subscription"]
            payment_intent_id = data_object["payment_intent"]

            payment_intent = await stripe_client.retrieve_payment_intent(
                payment_intent_id
            )

            await stripe_client.modify_subscription(
                stripe_subscription_id=stripe_subscription_id,
                default_payment_method=payment_intent.payment_method,
            )

    response.status_code = 200
    return response
