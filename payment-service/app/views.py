from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentRequestSerializer, PaymentSerializer


class PaymentProcessView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payment = Payment.objects.create(
            order_id=data["order_id"],
            amount=data["amount"],
            status="Failed" if data.get("simulate_failure") else "Success",
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentStatusListView(generics.ListAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.all().order_by("id")
        order_id = self.request.query_params.get("order_id")
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset


class PaymentStatusDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    lookup_url_kwarg = "order_id"

    def get_object(self):
        return get_object_or_404(Payment.objects.order_by("-id"), order_id=self.kwargs["order_id"])
