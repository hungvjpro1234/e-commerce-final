from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product_id", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user_id", "total_price", "status", "items"]


class CreateOrderSerializer(serializers.Serializer):
    address = serializers.CharField()
    simulate_payment_failure = serializers.BooleanField(required=False, default=False)


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]
