from django.urls import path

from .views import PaymentProcessView, PaymentStatusDetailView, PaymentStatusListView

urlpatterns = [
    path("payment/pay", PaymentProcessView.as_view(), name="payment-pay"),
    path("payment/status", PaymentStatusListView.as_view(), name="payment-status"),
    path("payment/status/<int:order_id>", PaymentStatusDetailView.as_view(), name="payment-status-detail"),
]

