from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user_id", "items"]


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class RemoveCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
