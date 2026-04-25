from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Shipment
from .serializers import ShipmentCreateSerializer, ShipmentSerializer


class ShipmentCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ShipmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shipment = Shipment.objects.create(**serializer.validated_data, status="Processing")
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)


class ShipmentStatusListView(generics.ListAPIView):
    serializer_class = ShipmentSerializer

    def get_queryset(self):
        queryset = Shipment.objects.all().order_by("id")
        order_id = self.request.query_params.get("order_id")
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset


class ShipmentStatusDetailView(generics.RetrieveAPIView):
    serializer_class = ShipmentSerializer
    lookup_url_kwarg = "order_id"

    def get_object(self):
        return get_object_or_404(Shipment.objects.order_by("-id"), order_id=self.kwargs["order_id"])
