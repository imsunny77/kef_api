from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q
from common.views import BasePagination
from product_management.models import Product
from product_management.serializers import ProductSerializer


class ProductListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination

    def get(self, request):
        products = Product.objects.filter(is_active=True, is_deleted=False)

        search = request.query_params.get("search", None)
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        category_id = request.query_params.get("category", None)
        if category_id:
            try:
                products = products.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass

        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(
            paginated_products, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)
