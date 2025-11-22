from django.urls import path
from order_management.views import OrderListView, OrderDetailView
from order_management.payment_views import (
    PaymentCreateView,
    PaymentConfirmView,
    StripeWebhookView,
)
from order_management.cart_views import CartView, CartItemView, CartToOrderView

app_name = "order_management"

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path(
        "orders/<int:order_id>/create-payment/",
        PaymentCreateView.as_view(),
        name="create-payment",
    ),
    path(
        "orders/<int:order_id>/confirm-payment/",
        PaymentConfirmView.as_view(),
        name="confirm-payment",
    ),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/items/<int:pk>/", CartItemView.as_view(), name="cart-item-detail"),
    path("cart/checkout/", CartToOrderView.as_view(), name="cart-checkout"),
]
