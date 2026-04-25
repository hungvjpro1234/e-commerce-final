from django.urls import path

from .views import ShipmentCreateView, ShipmentStatusDetailView, ShipmentStatusListView

urlpatterns = [
    path("shipping/create", ShipmentCreateView.as_view(), name="shipping-create"),
    path("shipping/status", ShipmentStatusListView.as_view(), name="shipping-status"),
    path("shipping/status/<int:order_id>", ShipmentStatusDetailView.as_view(), name="shipping-status-detail"),
]

