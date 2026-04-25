from django.urls import path

from .views import LoginView, RegisterView, UserListView

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("users/", UserListView.as_view(), name="user-list"),
]

