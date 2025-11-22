from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from order_management.models import Order, OrderItem
from order_management.serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderItemSerializer,
)
from common.email_service import send_order_confirmation_email, send_order_status_update_email


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_admin():
            orders = Order.objects.filter(is_active=True, is_deleted=False)
        else:
            orders = Order.objects.filter(
                customer=user, is_active=True, is_deleted=False
            )

        serializer = OrderSerializer(orders, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            order = serializer.save()
            send_order_confirmation_email(order)
            response_serializer = OrderSerializer(order, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        order = get_object_or_404(Order, pk=pk, is_active=True, is_deleted=False)
        if not user.is_admin() and order.customer != user:

            raise PermissionDenied("You do not have permission to access this order.")
        return order

    def get(self, request, pk):
        order = self.get_object(pk, request.user)
        serializer = OrderSerializer(order, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        order = self.get_object(pk, request.user)
        if not request.user.is_admin() and order.status != "pending":
            return Response(
                {"error": "Only pending orders can be updated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = order.status
        serializer = OrderSerializer(
            order, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            if old_status != order.status:
                send_order_status_update_email(order, old_status)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk, request.user)
        if not request.user.is_admin() and order.status != "pending":
            return Response(
                {"error": "Only pending orders can be deleted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.is_deleted = True
        order.is_active = False
        order.save()
        return Response(
            {"message": "Order deleted successfully"}, status=status.HTTP_200_OK
        )
