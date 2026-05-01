from django.urls import path

from .views import HealthCheckView, InternalShipmentCreateView, ShipmentStatusDetailView, ShipmentStatusListView

urlpatterns = [
    path("health", HealthCheckView.as_view(), name="health"),
    path("internal/shipping/create", InternalShipmentCreateView.as_view(), name="shipping-create"),
    path("shipping/status", ShipmentStatusListView.as_view(), name="shipping-status"),
    path("shipping/status/<int:order_id>", ShipmentStatusDetailView.as_view(), name="shipping-status-detail"),
]
