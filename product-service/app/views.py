from rest_framework import mixins, viewsets

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Product.objects.select_related("category").prefetch_related("book", "electronics", "fashion").order_by("id")
    serializer_class = ProductSerializer

