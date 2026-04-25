from django.urls import path

from .views import InternalShipmentCreateView, ShipmentStatusDetailView, ShipmentStatusListView

urlpatterns = [
    path("internal/shipping/create", InternalShipmentCreateView.as_view(), name="shipping-create"),
    path("shipping/status", ShipmentStatusListView.as_view(), name="shipping-status"),
    path("shipping/status/<int:order_id>", ShipmentStatusDetailView.as_view(), name="shipping-status-detail"),
]
