from django.urls import path

from .views import HealthCheckView, OrderListCreateView, OrderRetrieveView

urlpatterns = [
    path("health", HealthCheckView.as_view(), name="health"),
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>", OrderRetrieveView.as_view(), name="order-detail-no-slash"),
    path("orders/<int:pk>/", OrderRetrieveView.as_view(), name="order-detail"),
]
