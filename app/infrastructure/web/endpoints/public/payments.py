from fastapi import APIRouter, Body, Depends, Path
import stripe
from pydantic import conint

from app.usecases.schemas import payments
from app.settings import settings


payments_router = APIRouter(tags=["Payments"])

stripe.api_key = settings.stripe_secret_key

@payments_router.post(
    "/payment_intent",
    status_code=201,
    response_model=payments.CreatePaymentIntentResponse,
)
async def create_payment_intent(
    body: payments.CreatePaymentIntentRequest = Body(...),
) -> payments.CreatePaymentIntentResponse:
    """Creates a new payment intent 
       may not be needed when creating a subscription
    """

    params = {
        'amount': body.amount,
        'currency': body.currency, 
        'automatic_payment_methods': {
            'enabled': True,
        }
    }

    paymentIntent = stripe.PaymentIntent.create(**params)

    # Send PaymentIntent details to the front end.
    return payments.CreatePaymentIntentResponse(
        clientSecret=paymentIntent.client_secret
    )

@payments_router.post(
    "/create_subscription",
    status_code=201,
    response_model=payments.SubscriptionResponse
)
async def create_subscription(
    body: payments.SubscriptionRequest = Body(...),
) -> payments.SubscriptionResponse:
    # check to see if user_id has a valid customer_id
    user_id = body.userId
    customer_id = ''
    if False: # user_id has a customer_id
        customer_id = 'something' # get from database
    else: # create a new customer
        email = 'test' # get email from database
        customer = stripe.Customer.create(
            email=email # does pelleum support multiple accounts using same email
        )
        # save customer_id to database
        customer_id = customer.id

    try:
        # Create the subscription. Note we're expanding the Subscription's
        # latest invoice and that invoice's payment_intent
        # so we can pass it to the front end to confirm the payment
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                'price': body.priceId,
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        # return jsonify(subscriptionId=subscription.id, clientSecret=subscription.latest_invoice.payment_intent.client_secret)
        return payments.SubscriptionResponse(
            subscriptionId=subscription.id,
            clientSecret=subscription.latest_invoice.payment_intent.client_secret
        )

    except Exception as e:
        # return jsonify(error={'message': e.user_message}), 400
        return payments.SubscriptionResponse(
            # error message
        )
    
# can get subscription from Stripe customer object
# or can store subscription_ids from pelleum database
@payments_router.post(
    "/cancel_subscription",
    status_code=201,
    response_model=payments.SubscriptionResponse
)
async def cancel_subscription(
    body: payments.SubscriptionRequest = Body(...),
) -> payments.SubscriptionResponse:
    try:
        # Cancel the subscription by deleting it
        deletedSubscription = stripe.Subscription.delete(body.subscriptionId)
        # return jsonify(subscription=deletedSubscription)
        return payments.SubscriptionResponse(
            subscriptionId=deletedSubscription.id,
            # send subscription status perhaps
        )
    except Exception as e:
        return payments.SubscriptionResponse(
            # error message
        )

@payments_router.get(
    "/subscriptions/{user_id}", # can we get active user? - maybe dont need query param
    status_code=200,
    response_model=payments.SubscriptionResponse
)
async def get_subscriptions(
    user_id: conint(gt=0, lt=100000000000) = Path(...),
) -> payments.SubscriptionResponse:
    # get customer_id associated with user_id
    customer_id = ''
    # call stripe to get customer object associated with 
    # customer = 
    # check to see which subscriptions customer has active 
    # customer.subscriptions

@payments.router.post(
    "/webhook_received",
    status_code=201,
    response_model=payments.WebhookResponse,
)
async def webhook_received(
    body: payments.WebhookRequest = Body(...),
) -> payments.WebhookResponse:
    """Listens for webhook calls from Stripe"""

    webhook_secret = settings.stripe_webhook_secret
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    if event_type == 'payment_intent.succeeded':
        print('💰 Payment received!')
        # Fulfill any orders, e-mail receipts, etc
        # To cancel the payment you will need to issue a Refund (https://stripe.com/docs/api/refunds)
    elif event_type == 'payment_intent.payment_failed':
        print('❌ Payment failed.')
    return jsonify({'status': 'success'})
