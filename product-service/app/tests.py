from django.db.models import ForeignKey, OneToOneField
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Product


class ProductModelTests(TestCase):
    def test_product_has_internal_foreign_key(self):
        field = Product._meta.get_field("category")
        self.assertIsInstance(field, ForeignKey)

    def test_category_product_creation(self):
        category = Category.objects.create(name="Books")
        product = Product.objects.create(name="Clean Code", price=10.5, stock=5, category=category)
        self.assertEqual(product.category.name, "Books")


class ProductApiTests(TestCase):
    def test_list_products(self):
        client = APIClient()
        response = client.get("/products/")
        self.assertEqual(response.status_code, 200)

