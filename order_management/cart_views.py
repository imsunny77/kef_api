from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from order_management.models import Cart, CartItem, Order, OrderItem
from order_management.serializers import (
    CartSerializer,
    CartItemSerializer,
    CartItemCreateSerializer,
    CartToOrderSerializer,
    OrderSerializer,
)
from product_management.models import Product


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            product = serializer.validated_data["product"]
            quantity = serializer.validated_data["quantity"]
            price = serializer.validated_data["price"]

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": quantity, "price": price},
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.price = price
                cart_item.save()

            response_serializer = CartItemSerializer(cart_item, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response(
            {"message": "Cart cleared successfully"}, status=status.HTTP_200_OK
        )


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        cart_item = get_object_or_404(
            CartItem, pk=pk, cart__user=user, is_active=True, is_deleted=False
        )
        return cart_item

    def put(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        quantity = request.data.get("quantity")
        
        if quantity is None:
            return Response(
                {"quantity": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity < 1:
            return Response(
                {"quantity": ["Quantity must be at least 1."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if cart_item.product.stock_quantity < quantity:
            return Response(
                {"error": "Insufficient stock"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        quantity = request.data.get("quantity", cart_item.quantity)
        
        if quantity < 1:
            return Response(
                {"quantity": ["Quantity must be at least 1."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if cart_item.product.stock_quantity < quantity:
            return Response(
                {"error": "Insufficient stock"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        cart_item.delete()
        return Response(
            {"message": "Cart item removed successfully"}, status=status.HTTP_200_OK
        )


class CartToOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        if not cart.items.exists():
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CartToOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = serializer.validated_data.get("shipping_address", "")
        billing_address = serializer.validated_data.get("billing_address", "")
        clear_cart = serializer.validated_data.get("clear_cart", True)

        order = Order.objects.create(
            customer=request.user,
            shipping_address=shipping_address,
            billing_address=billing_address,
        )

        for cart_item in cart.items.all():
            if cart_item.product.stock_quantity < cart_item.quantity:
                order.delete()
                return Response(
                    {
                        "error": f"Insufficient stock for {cart_item.product.name}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item.product.stock_quantity -= cart_item.quantity
            cart_item.product.save()

            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.price,
            )

        order.calculate_total()

        if clear_cart:
            cart.items.all().delete()

        response_serializer = OrderSerializer(order, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


