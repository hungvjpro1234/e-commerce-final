from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import HealthCheckView, LoginView, RegisterView, UserDetailView, UserListView

urlpatterns = [
    path("health", HealthCheckView.as_view(), name="health"),
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
