from django.urls import path
from administration.views import RegisterView, LoginView

app_name = "administration"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]
