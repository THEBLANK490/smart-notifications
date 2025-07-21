from django.urls import path

from apps.accounts.api.views import UserLoginView, UserRegistrationView

app_name = "user"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-create"),
    path("login/", UserLoginView.as_view(), name="user-login"),
]