from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum
from order_management.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at", "is_active")
    search_fields = ("order_number", "customer__email")
    readonly_fields = ("order_number", "total_amount", "created_at", "updated_at", "crm_sync_status")
    inlines = [OrderItemInline]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        from django.urls import reverse
        extra_context['reports_url'] = reverse('admin:order_management_reports')
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        from django.contrib import admin
        custom_urls = [
            path("reports/", admin.site.admin_view(self.reports_view), name="order_management_reports"),
        ]
        return custom_urls + urls

    def reports_view(self, request):
        if not request.user.is_admin():
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("You do not have permission to access this page.")

        orders = Order.objects.filter(is_active=True, is_deleted=False)
        
        total_orders = orders.count()
        total_revenue = orders.filter(status="completed").aggregate(
            total=Sum("total_amount")
        )["total"] or 0
        
        paid_orders = orders.filter(status="completed").count()
        pending_orders = orders.filter(status="pending").count()

        from django.contrib import admin
        context = {
            **admin.site.each_context(request),
            "title": "Order Reports Summary",
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "paid_orders": paid_orders,
            "pending_orders": pending_orders,
        }

        return render(request, "admin/order_management/reports.html", context)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price", "subtotal")
    list_filter = ("created_at",)
    search_fields = ("order__order_number", "product__name")
