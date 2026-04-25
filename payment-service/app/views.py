import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import InternalServiceAuthentication, get_request_user_id, is_staff_or_admin
from .models import Payment
from .serializers import PaymentRequestSerializer, PaymentSerializer


logger = logging.getLogger(__name__)


class InternalPaymentProcessView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payment = Payment.objects.create(
            order_id=data["order_id"],
            user_id=data["user_id"],
            amount=data["amount"],
            status="Failed" if data.get("simulate_failure") else "Success",
        )
        logger.info(
            "payment.processed correlation_id=%s order_id=%s user_id=%s status=%s",
            request.headers.get("X-Correlation-ID", ""),
            payment.order_id,
            payment.user_id,
            payment.status,
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentStatusListView(generics.ListAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.all().order_by("id")
        if is_staff_or_admin(self.request):
            order_id = self.request.query_params.get("order_id")
            if order_id:
                queryset = queryset.filter(order_id=order_id)
            return queryset
        return queryset.filter(user_id=get_request_user_id(self.request))


class PaymentStatusDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    lookup_url_kwarg = "order_id"

    def get_object(self):
        payment = get_object_or_404(Payment.objects.order_by("-id"), order_id=self.kwargs["order_id"])
        if is_staff_or_admin(self.request):
            return payment
        if payment.user_id != get_request_user_id(self.request):
            raise NotFound()
        return payment
