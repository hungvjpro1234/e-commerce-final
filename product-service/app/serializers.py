from rest_framework import serializers

from .models import Book, Category, Electronics, Fashion, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["author", "publisher", "isbn"]


class ElectronicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electronics
        fields = ["brand", "warranty"]


class FashionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fashion
        fields = ["size", "color"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    detail_type = serializers.ChoiceField(
        choices=[("book", "book"), ("electronics", "electronics"), ("fashion", "fashion")],
        write_only=True,
        required=False,
    )
    detail = serializers.DictField(write_only=True, required=False)
    book = BookSerializer(read_only=True)
    electronics = ElectronicsSerializer(read_only=True)
    fashion = FashionSerializer(read_only=True)
    category_data = CategorySerializer(source="category", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "stock",
            "category",
            "category_data",
            "detail_type",
            "detail",
            "book",
            "electronics",
            "fashion",
        ]

    def create(self, validated_data):
        detail_type = validated_data.pop("detail_type", None)
        detail = validated_data.pop("detail", {})
        product = Product.objects.create(**validated_data)
        if detail_type == "book":
            Book.objects.create(product=product, **detail)
        elif detail_type == "electronics":
            Electronics.objects.create(product=product, **detail)
        elif detail_type == "fashion":
            Fashion.objects.create(product=product, **detail)
        return product

