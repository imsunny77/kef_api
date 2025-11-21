from rest_framework import serializers
from .models import Order, OrderItem
from product_management.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "quantity",
            "price",
            "subtotal",
            "created_at",
        )
        read_only_fields = ("subtotal", "created_at")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "customer",
            "customer_email",
            "total_amount",
            "status",
            "shipping_address",
            "billing_address",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("order_number", "total_amount", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        order = Order.objects.create(**validated_data)
        return order


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        from product_management.models import Product
        product_id = attrs.get("product_id")
        quantity = attrs.get("quantity", 1)

        try:
            product = Product.objects.get(
                id=product_id, is_active=True, is_deleted=False
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive")

        if product.stock_quantity < quantity:
            raise serializers.ValidationError("Insufficient stock")

        attrs["product"] = product
        attrs["price"] = product.price
        return attrs


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=False, allow_blank=True)
    billing_address = serializers.CharField(required=False, allow_blank=True)
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        customer = self.context["request"].user
        order = Order.objects.create(customer=customer, **validated_data)

        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]
            
            product.stock_quantity -= quantity
            product.save()
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item_data["price"],
            )

        return order

