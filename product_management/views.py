from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q
from collections import defaultdict
from common.views import BasePagination
from product_management.models import Product, Category
from product_management.serializers import ProductSerializer, CategorySerializer


class ProductListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination

    def get(self, request):
        products = (
            Product.objects.select_related("category")
            .order_by("category__name", "name")
            .filter(is_active=True, is_deleted=False)
        )

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

    def post(self, request):
        if request.user.is_customer():
            raise PermissionDenied("Only admins can create products")

        serializer = ProductSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                ProductSerializer(product, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk, is_active=True, is_deleted=False)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can update products")

        product = self.get_object(pk)
        serializer = ProductSerializer(
            product, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can delete products")

        product = self.get_object(pk)
        product.is_deleted = True
        product.is_active = False
        product.save()
        return Response(
            {"message": "Product deleted successfully"}, status=status.HTTP_200_OK
        )


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination

    def get(self, request):
        categories = Category.objects.filter(is_active=True, is_deleted=False)
        paginator = self.pagination_class()
        paginated_categories = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(paginated_categories, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can create categories")

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(
                CategorySerializer(category).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk, is_active=True, is_deleted=False)

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can update categories")

        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_admin():
            raise PermissionDenied("Only admins can delete categories")

        category = self.get_object(pk)
        category.is_deleted = True
        category.is_active = False
        category.save()
        return Response(
            {"message": "Category deleted successfully"}, status=status.HTTP_200_OK
        )
