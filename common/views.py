from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination


# Create your views here.
class BasePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
