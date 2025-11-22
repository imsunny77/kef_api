import stripe
import os
from decimal import Decimal

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")


def create_customer(email, name=None):
    try:
        customer = stripe.Customer.create(email=email, name=name)
        return customer.id
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to create Stripe customer: {str(e)}")


def create_payment_intent(amount, currency="usd", customer_id=None, metadata=None):
    try:
        amount_in_cents = int(float(amount) * 100)
        intent_data = {
            "amount": amount_in_cents,
            "currency": currency,
            "automatic_payment_methods": {"enabled": True},
        }
        
        if customer_id:
            intent_data["customer"] = customer_id
        
        if metadata:
            intent_data["metadata"] = metadata

        intent = stripe.PaymentIntent.create(**intent_data)
        return intent
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to create payment intent: {str(e)}")


def confirm_payment_intent(payment_intent_id):
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return intent
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to retrieve payment intent: {str(e)}")


def cancel_payment_intent(payment_intent_id):
    try:
        intent = stripe.PaymentIntent.cancel(payment_intent_id)
        return intent
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to cancel payment intent: {str(e)}")



