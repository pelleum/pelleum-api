from fastapi import APIRouter, Body
import stripe

from app.usecases.schemas import payments
from app.settings import settings


payments_router = APIRouter(tags=["Payments"])

stripe.api_key = settings.stripe_secret_key

@payments_router.post(
    "",
    status_code=201,
    response_model=payments.CreatePaymentIntentResponse,
)
async def create_payment_intent(
    body: payments.CreatePaymentIntentRequest = Body(...),
) -> payments.CreatePaymentIntentResponse:
    """Creates a new payment intent"""

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

@payments.router.post(
    "/webhook",
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
