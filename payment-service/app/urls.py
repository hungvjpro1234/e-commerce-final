from django.urls import path

from .views import HealthCheckView, InternalPaymentProcessView, PaymentStatusDetailView, PaymentStatusListView

urlpatterns = [
    path("health", HealthCheckView.as_view(), name="health"),
    path("internal/payment/pay", InternalPaymentProcessView.as_view(), name="payment-pay"),
    path("payment/status", PaymentStatusListView.as_view(), name="payment-status"),
    path("payment/status/<int:order_id>", PaymentStatusDetailView.as_view(), name="payment-status-detail"),
]
