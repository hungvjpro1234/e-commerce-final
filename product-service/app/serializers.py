from rest_framework import serializers

from .models import Category, Product
from .product_types import PRODUCT_TYPE_SCHEMAS, get_product_type_schema


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_data = CategorySerializer(source="category", read_only=True)
    detail_type = serializers.CharField()
    detail = serializers.DictField()

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
        ]

    def validate_detail_type(self, value):
        if value not in PRODUCT_TYPE_SCHEMAS:
            raise serializers.ValidationError("Unsupported detail_type.")
        return value

    def validate(self, attrs):
        detail_type = attrs.get("detail_type")
        detail = attrs.get("detail")

        if self.instance:
            detail_type = detail_type or self.instance.detail_type
            detail = detail if detail is not None else self.instance.detail

        if not detail_type:
            raise serializers.ValidationError({"detail_type": "This field is required."})
        if detail is None:
            raise serializers.ValidationError({"detail": "This field is required."})

        attrs["detail"] = self._validate_detail(detail_type, detail)
        return attrs

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def _validate_detail(self, detail_type, detail):
        schema = get_product_type_schema(detail_type)
        if not isinstance(detail, dict):
            raise serializers.ValidationError({"detail": "Detail must be an object."})

        errors = {}
        normalized_detail = {}
        for field in schema["fields"]:
            name = field["name"]
            value = detail.get(name)

            if field.get("required") and value in (None, ""):
                errors[name] = "This field is required."
                continue

            if value is None:
                continue

            field_type = field["type"]
            if field_type == "string":
                if not isinstance(value, str):
                    errors[name] = "Must be a string."
                    continue
                normalized_detail[name] = value.strip()
            elif field_type == "number":
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    errors[name] = "Must be a number."
                    continue
                normalized_detail[name] = value
            elif field_type == "boolean":
                if not isinstance(value, bool):
                    errors[name] = "Must be a boolean."
                    continue
                normalized_detail[name] = value

        extra_fields = sorted(set(detail.keys()) - {field["name"] for field in schema["fields"]})
        if extra_fields:
            errors["non_field_errors"] = [f"Unknown detail fields: {', '.join(extra_fields)}"]

        if errors:
            raise serializers.ValidationError({"detail": errors})
        return normalized_detail
