from django.urls import path
from .views import ProductListView

app_name = "product_management"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
]
