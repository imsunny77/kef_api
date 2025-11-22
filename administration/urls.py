from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from administration.views import RegisterView, LoginView

app_name = "administration"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
