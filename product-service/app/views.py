from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .auth import InternalServiceAuthentication, IsAdmin
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [AllowAny()]
        return [IsAdmin()]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").prefetch_related("book", "electronics", "fashion").order_by("id")
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [AllowAny()]
        return [IsAdmin()]


class InternalProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related("category").prefetch_related("book", "electronics", "fashion").order_by("id")
    serializer_class = ProductSerializer
    authentication_classes = [InternalServiceAuthentication]
