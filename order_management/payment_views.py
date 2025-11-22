from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import stripe
from decouple import config
import requests
from order_management.models import Order
from order_management.serializers import OrderSerializer
from order_management.stripe_service import confirm_payment_intent, create_customer, create_payment_intent

stripe.api_key = config("STRIPE_SECRET_KEY", default="")


def sync_to_crm(order):
    try:
        response = requests.post(
            "https://dummyjson.com/posts/add",
            headers={"Content-Type": "application/json"},
            json={
                "title": f"Order {order.order_number} - {order.customer.email}",
                "userId": order.customer.id,
                "body": f"Order ID: {order.id}, Amount: ${order.total_amount}, Customer: {order.customer.email}, Status: {order.status}",
            },
            timeout=10
        )
        if response.status_code == 200 or response.status_code == 201:
            order.crm_sync_status = "success"
        else:
            order.crm_sync_status = "failed"
    except Exception:
        order.crm_sync_status = "failed"
    finally:
        order.save()


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, is_active=True, is_deleted=False)

        if not request.user.is_admin() and order.customer != request.user:
            raise PermissionDenied("You do not have permission to access this order.")

        if order.status != "pending":
            return Response(
                {"error": "Only pending orders can initiate payment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if not order.stripe_customer_id:
                stripe_customer_id = create_customer(
                    email=order.customer.email,
                    name=f"{order.customer.first_name} {order.customer.last_name}".strip() or None
                )
                order.stripe_customer_id = stripe_customer_id

            if not order.stripe_payment_intent_id:
                payment_intent = create_payment_intent(
                    amount=float(order.total_amount),
                    customer_id=order.stripe_customer_id,
                    metadata={
                        "order_id": str(order.id),
                        "order_number": order.order_number,
                    }
                )
                order.stripe_payment_intent_id = payment_intent.id
                order.save()
            else:
                payment_intent = confirm_payment_intent(order.stripe_payment_intent_id)

            return Response(
                {
                    "client_secret": payment_intent.client_secret,
                    "payment_intent_id": payment_intent.id,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, is_active=True, is_deleted=False)

        if not request.user.is_admin() and order.customer != request.user:
            raise PermissionDenied("You do not have permission to access this order.")

        if not order.stripe_payment_intent_id:
            return Response(
                {"error": "Payment intent not found for this order"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            intent = confirm_payment_intent(order.stripe_payment_intent_id)

            if intent.status == "succeeded":
                order.status = "completed"
                order.save()
                sync_to_crm(order)
                serializer = OrderSerializer(order, context={"request": request})
                return Response(
                    {
                        "message": "Payment confirmed successfully",
                        "order": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            elif intent.status == "requires_payment_method":
                return Response(
                    {
                        "error": "Payment requires a payment method",
                        "client_secret": intent.client_secret,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif intent.status == "requires_confirmation":
                return Response(
                    {
                        "error": "Payment requires confirmation",
                        "client_secret": intent.client_secret,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return Response(
                    {
                        "error": f"Payment status: {intent.status}",
                        "client_secret": intent.client_secret,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        webhook_secret = config("STRIPE_WEBHOOK_SECRET", default="")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError:
            return JsonResponse({"error": "Invalid payload"}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({"error": "Invalid signature"}, status=400)

        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            self._handle_payment_success(payment_intent)
        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            self._handle_payment_failure(payment_intent)
        elif event["type"] == "payment_intent.canceled":
            payment_intent = event["data"]["object"]
            self._handle_payment_canceled(payment_intent)

        return JsonResponse({"status": "success"})

    def _handle_payment_success(self, payment_intent):
        try:
            order = Order.objects.get(
                stripe_payment_intent_id=payment_intent["id"],
                is_active=True,
                is_deleted=False,
            )
            order.status = "completed"
            order.save()
            sync_to_crm(order)
        except Order.DoesNotExist:
            pass

    def _handle_payment_failure(self, payment_intent):
        try:
            order = Order.objects.get(
                stripe_payment_intent_id=payment_intent["id"],
                is_active=True,
                is_deleted=False,
            )
            if order.status == "pending":
                order.status = "cancelled"
                order.save()
        except Order.DoesNotExist:
            pass

    def _handle_payment_canceled(self, payment_intent):
        try:
            order = Order.objects.get(
                stripe_payment_intent_id=payment_intent["id"],
                is_active=True,
                is_deleted=False,
            )
            if order.status == "pending":
                order.status = "cancelled"
                order.save()
        except Order.DoesNotExist:
            pass
