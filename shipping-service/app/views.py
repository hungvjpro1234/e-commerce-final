import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import InternalServiceAuthentication, get_request_user_id, is_staff_or_admin
from .models import Shipment
from .serializers import ShipmentCreateSerializer, ShipmentSerializer, ShipmentStatusUpdateSerializer


logger = logging.getLogger(__name__)


class InternalShipmentCreateView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = ShipmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipment = Shipment.objects.create(**serializer.validated_data, status="Processing")
        logger.info(
            "shipment.created correlation_id=%s order_id=%s user_id=%s status=%s",
            request.headers.get("X-Correlation-ID", ""),
            shipment.order_id,
            shipment.user_id,
            shipment.status,
        )
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)


class ShipmentStatusListView(generics.ListAPIView):
    serializer_class = ShipmentSerializer

    def get_queryset(self):
        queryset = Shipment.objects.all().order_by("id")
        if is_staff_or_admin(self.request):
            order_id = self.request.query_params.get("order_id")
            if order_id:
                queryset = queryset.filter(order_id=order_id)
            return queryset
        return queryset.filter(user_id=get_request_user_id(self.request))


class ShipmentStatusDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ShipmentSerializer
    lookup_url_kwarg = "order_id"

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return ShipmentStatusUpdateSerializer
        return super().get_serializer_class()

    def get_object(self):
        shipment = get_object_or_404(Shipment.objects.order_by("-id"), order_id=self.kwargs["order_id"])
        if is_staff_or_admin(self.request):
            return shipment
        if shipment.user_id != get_request_user_id(self.request):
            raise NotFound()
        return shipment

    def update(self, request, *args, **kwargs):
        if not is_staff_or_admin(request):
            raise PermissionDenied("Only staff or admin can update shipping status.")
        return super().update(request, *args, **kwargs)
