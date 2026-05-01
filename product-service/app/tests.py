import jwt
from django.conf import settings
from django.db.models import ForeignKey
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APIClient

from .models import Category, Product
from .serializers import ProductSerializer


class ProductModelTests(TestCase):
    def test_product_has_internal_foreign_key(self):
        field = Product._meta.get_field("category")
        self.assertIsInstance(field, ForeignKey)

    def test_category_product_creation(self):
        category = Category.objects.create(name="Books")
        product = Product.objects.create(
            name="Clean Code",
            price=10.5,
            stock=5,
            category=category,
            detail_type="book",
            detail={"author": "Robert C. Martin", "publisher": "Prentice Hall", "isbn": "9780132350884"},
        )
        self.assertEqual(product.category.name, "Books")
        self.assertEqual(product.detail_type, "book")


class ProductSerializerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="General")

    def test_accepts_existing_type_schema(self):
        serializer = ProductSerializer(
            data={
                "name": "Noise Cancel Earbuds",
                "price": 149,
                "stock": 8,
                "category": self.category.id,
                "detail_type": "electronics",
                "detail": {"brand": "SoundPeak", "warranty_months": 12, "model": "NC-E2"},
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_accepts_new_type_schema(self):
        serializer = ProductSerializer(
            data={
                "name": "Organic Granola",
                "price": 8.5,
                "stock": 20,
                "category": self.category.id,
                "detail_type": "grocery",
                "detail": {"weight_grams": 500, "expiry_days": 180, "organic": True},
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_invalid_detail_payload(self):
        serializer = ProductSerializer(
            data={
                "name": "Marker Set Pro",
                "price": 15,
                "stock": 12,
                "category": self.category.id,
                "detail_type": "office",
                "detail": {"brand": "WriteWell", "pack_size": "12", "color": "Mixed"},
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)


class ProductApiTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Beauty")
        self.product = Product.objects.create(
            name="Hydrating Serum",
            price=27,
            stock=40,
            category=self.category,
            detail_type="beauty",
            detail={"brand": "GlowLab", "skin_type": "Dry", "volume_ml": 30},
        )

    def _admin_client(self):
        token = AccessToken()
        token["user_id"] = 1
        token["id"] = 1
        token["role"] = "admin"
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_list_products(self):
        client = APIClient()
        response = client.get("/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["detail_type"], "beauty")
        self.assertEqual(response.data[0]["detail"]["brand"], "GlowLab")

    def test_customer_cannot_create_product(self):
        token = AccessToken()
        token["user_id"] = 1
        token["id"] = 1
        token["role"] = "customer"

        client = APIClient()
        response = client.post(
            "/products/",
            {
                "name": "Test",
                "price": 10,
                "stock": 5,
                "category": self.category.id,
                "detail_type": "beauty",
                "detail": {"brand": "GlowLab", "skin_type": "Dry", "volume_ml": 30},
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_product_with_new_detail_type(self):
        client = self._admin_client()
        response = client.post(
            "/products/",
            {
                "name": "Dog Bowl Steel",
                "price": 18,
                "stock": 22,
                "category": self.category.id,
                "detail_type": "pet-supplies",
                "detail": {"pet_type": "Dog", "size": "Medium", "weight_grams": 450},
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["detail_type"], "pet-supplies")

    def test_patch_updates_detail(self):
        client = self._admin_client()
        response = client.patch(
            f"/products/{self.product.id}/",
            {"detail": {"brand": "GlowLab", "skin_type": "Sensitive", "volume_ml": 50}},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.detail["skin_type"], "Sensitive")

    def test_internal_endpoint_returns_base_fields_for_orders(self):
        token = jwt.encode(
            {
                "service": "order-service",
                "aud": settings.INTERNAL_SERVICE_AUDIENCE,
                "iss": settings.INTERNAL_SERVICE_ISSUER,
            },
            settings.INTERNAL_SERVICE_JWT_SECRET,
            algorithm=settings.INTERNAL_SERVICE_JWT_ALGORITHM,
        )
        client = APIClient()
        response = client.get(f"/internal/products/{self.product.id}/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("price", response.data)
        self.assertIn("stock", response.data)
        self.assertIn("detail_type", response.data)
