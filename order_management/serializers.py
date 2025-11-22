from rest_framework import serializers
from order_management.models import Order, OrderItem, Cart, CartItem
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
    client_secret = serializers.SerializerMethodField()

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
            "stripe_payment_intent_id",
            "client_secret",
            "crm_sync_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "order_number",
            "total_amount",
            "stripe_payment_intent_id",
            "client_secret",
            "crm_sync_status",
            "created_at",
            "updated_at",
        )

    def get_client_secret(self, obj):
        if obj.stripe_payment_intent_id:
            try:
                from order_management.stripe_service import confirm_payment_intent

                intent = confirm_payment_intent(obj.stripe_payment_intent_id)
                return intent.client_secret
            except Exception:
                return None
        return None

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
    items = OrderItemCreateSerializer(many=True, required=False)
    cart_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        cart_id = attrs.get("cart_id")

        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user=self.context["request"].user)
                if not cart.items.exists():
                    raise serializers.ValidationError("Cart is empty")
                attrs["cart"] = cart
            except Cart.DoesNotExist:
                raise serializers.ValidationError("Cart not found or access denied")

        return attrs

    def validate_items(self, value):
        if value and not value:
            raise serializers.ValidationError("Order must have at least one item")
        return value

    def create(self, validated_data):
        customer = self.context["request"].user
        shipping_address = validated_data.get("shipping_address", "")
        billing_address = validated_data.get("billing_address", "")
        cart = validated_data.get("cart")
        items_data = validated_data.get("items", [])

        order = Order.objects.create(
            customer=customer,
            shipping_address=shipping_address,
            billing_address=billing_address,
        )

        if cart:
            for cart_item in cart.items.all():
                if cart_item.product.stock_quantity < cart_item.quantity:
                    order.delete()
                    raise serializers.ValidationError(
                        f"Insufficient stock for {cart_item.product.name}"
                    )

                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()

                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                )

            cart.items.all().delete()
        else:
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

        order.calculate_total()

        return order


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "quantity",
            "price",
            "subtotal",
            "created_at",
        )
        read_only_fields = ("price", "subtotal", "created_at")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "items",
            "total_amount",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_total_amount(self, obj):
        return obj.calculate_total()


class CartItemCreateSerializer(serializers.Serializer):
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


class CartToOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=False, allow_blank=True)
    billing_address = serializers.CharField(required=False, allow_blank=True)
    clear_cart = serializers.BooleanField(default=True)
