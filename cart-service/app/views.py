from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import InternalServiceAuthentication, get_request_user_id
from .models import Cart, CartItem
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    RemoveCartItemSerializer,
    UpdateCartItemSerializer,
)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        cart, _ = Cart.objects.get_or_create(user_id=get_request_user_id(request))
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=data["product_id"],
            defaults={"quantity": data["quantity"]},
        )
        if not created:
            item.quantity += data["quantity"]
            item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer

    def get_object(self):
        return get_object_or_404(Cart.objects.prefetch_related("items"), user_id=get_request_user_id(self.request))


class UpdateCartView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        cart = get_object_or_404(Cart, user_id=get_request_user_id(request))
        item = get_object_or_404(CartItem, cart=cart, product_id=data["product_id"])
        item.quantity = data["quantity"]
        item.save()
        return Response(CartSerializer(cart).data)


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        serializer = RemoveCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        cart = get_object_or_404(Cart, user_id=get_request_user_id(request))
        item = get_object_or_404(CartItem, cart=cart, product_id=data["product_id"])
        item.delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user_id=get_request_user_id(request))
        cart.items.all().delete()
        return Response({"detail": "Cart cleared."}, status=status.HTTP_200_OK)


class InternalCartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    authentication_classes = [InternalServiceAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Cart.objects.prefetch_related("items"), user_id=self.kwargs["user_id"])


class InternalClearCartView(APIView):
    authentication_classes = [InternalServiceAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user_id=self.kwargs["user_id"])
        cart.items.all().delete()
        return Response({"detail": "Cart cleared."}, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response({"service": "cart-service", "status": "ok"})
