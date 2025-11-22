from django.urls import path
from product_management.views import (
    ProductListView,
    ProductDetailView,
    CategoryListView,
    CategoryDetailView,
)

app_name = "product_management"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
]
