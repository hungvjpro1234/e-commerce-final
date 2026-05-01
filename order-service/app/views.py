import logging

from django.db import transaction
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import get_correlation_id, get_request_user_id, is_staff_or_admin
from .models import Order, OrderItem
from .serializers import CreateOrderSerializer, OrderSerializer, UpdateOrderStatusSerializer
from .service_clients import ServiceClientError, clear_cart, create_payment, create_shipment, get_cart, get_product


logger = logging.getLogger(__name__)


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.prefetch_related("items").order_by("id")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_staff_or_admin(self.request):
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            return queryset
        return queryset.filter(user_id=get_request_user_id(self.request))

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user_id = get_request_user_id(request)
        correlation_id = get_correlation_id(request)

        try:
            cart_data = get_cart(user_id, correlation_id)
        except ServiceClientError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        items = cart_data.get("items", [])
        if not items:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0
        product_snapshots = []
        try:
            for item in items:
                product = get_product(item["product_id"], correlation_id)
                if product["stock"] < item["quantity"]:
                    return Response(
                        {"detail": f"Insufficient stock for product {item['product_id']}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                line_total = product["price"] * item["quantity"]
                total_price += line_total
                product_snapshots.append(item)
        except ServiceClientError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        logger.info("order.create.start correlation_id=%s user_id=%s item_count=%s", correlation_id, user_id, len(items))

        with transaction.atomic():
            order = Order.objects.create(user_id=user_id, total_price=total_price, status="Pending")
            for item in product_snapshots:
                OrderItem.objects.create(order=order, product_id=item["product_id"], quantity=item["quantity"])

            try:
                payment = create_payment(order.id, user_id, total_price, correlation_id, data["simulate_payment_failure"])
            except ServiceClientError as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

            if payment["status"] != "Success":
                order.status = "Cancelled"
                order.save(update_fields=["status"])
                return Response(OrderSerializer(order).data, status=status.HTTP_402_PAYMENT_REQUIRED)

            order.status = "Paid"
            order.save(update_fields=["status"])

            try:
                shipment = create_shipment(order.id, user_id, data["address"], correlation_id)
            except ServiceClientError as exc:
                return Response(
                    {"detail": str(exc), "order": OrderSerializer(order).data},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            if shipment["status"] in {"Processing", "Shipping", "Delivered"}:
                order.status = "Shipping"
                order.save(update_fields=["status"])

            try:
                clear_cart(user_id, correlation_id)
            except ServiceClientError as exc:
                return Response(
                    {"detail": str(exc), "order": OrderSerializer(order).data},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        logger.info("order.create.complete correlation_id=%s order_id=%s status=%s", correlation_id, order.id, order.status)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderRetrieveView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.prefetch_related("items")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return UpdateOrderStatusSerializer
        return super().get_serializer_class()

    def get_object(self):
        order = super().get_object()
        if is_staff_or_admin(self.request):
            return order
        if order.user_id != get_request_user_id(self.request):
            raise NotFound()
        return order

    def update(self, request, *args, **kwargs):
        if not is_staff_or_admin(request):
            raise PermissionDenied("Only staff or admin can update order status.")
        return super().update(request, *args, **kwargs)


class HealthCheckView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response({"service": "order-service", "status": "ok"})
