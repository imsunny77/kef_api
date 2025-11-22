from django.db import models
from django.conf import settings
from decimal import Decimal
import time
from common.models import BaseModel
from product_management.models import Product


class Order(BaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    shipping_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    crm_sync_status = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number} - {self.customer.email}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{int(time.time())}"
        
        if self.pk:
            try:
                old_order = Order.objects.get(pk=self.pk)
                if old_order.status != "cancelled" and self.status == "cancelled":
                    self._restore_stock()
                elif old_order.status == "cancelled" and self.status != "cancelled":
                    self._decrement_stock()
            except Order.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def _restore_stock(self):
        for item in self.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save()
    
    def _decrement_stock(self):
        for item in self.items.all():
            if item.product.stock_quantity >= item.quantity:
                item.product.stock_quantity -= item.quantity
                item.product.save()

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.quantity} x {self.product.name} - Order {self.order.order_number}"
        )

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_item = OrderItem.objects.get(pk=self.pk)
                if old_item.quantity != self.quantity:
                    old_item.product.stock_quantity += old_item.quantity
                    if old_item.product.stock_quantity >= self.quantity:
                        old_item.product.stock_quantity -= self.quantity
                    old_item.product.save()
            except OrderItem.DoesNotExist:
                pass
        
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
        self.order.calculate_total()
    
    def delete(self, *args, **kwargs):
        if self.order.status != "cancelled":
            self.product.stock_quantity += self.quantity
            self.product.save()
        super().delete(*args, **kwargs)
