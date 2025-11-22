from rest_framework import serializers
from product_management.models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True, is_deleted=False),
        source="category",
        write_only=True,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "category",
            "category_id",
            "price",
            "stock_quantity",
            "image",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("slug", "created_at", "updated_at")
