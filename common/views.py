from django.shortcuts import render
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, Q
from order_management.models import Order


class BasePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ReportsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin():
            return Response(
                {"error": "Only admins can access reports"},
                status=status.HTTP_403_FORBIDDEN
            )

        orders = Order.objects.filter(is_active=True, is_deleted=False)
        
        total_orders = orders.count()
        total_revenue = orders.filter(status="completed").aggregate(
            total=Sum("total_amount")
        )["total"] or 0
        
        paid_orders = orders.filter(status="completed").count()
        pending_orders = orders.filter(status="pending").count()

        return Response({
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "paid_orders": paid_orders,
            "pending_orders": pending_orders,
        })
