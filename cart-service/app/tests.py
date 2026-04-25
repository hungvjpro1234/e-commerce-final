from django.db.models import ForeignKey
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APIClient

from .models import Cart, CartItem


class CartModelTests(TestCase):
    def test_cart_item_has_internal_foreign_key(self):
        field = CartItem._meta.get_field("cart")
        self.assertIsInstance(field, ForeignKey)


class CartApiTests(TestCase):
    def _auth_headers(self, user_id=1, role="customer"):
        token = AccessToken()
        token["user_id"] = user_id
        token["id"] = user_id
        token["role"] = role
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_add_to_cart(self):
        client = APIClient()
        response = client.post("/cart/add", {"product_id": 1, "quantity": 2}, format="json", **self._auth_headers())
        self.assertEqual(response.status_code, 201)

    def test_clear_cart(self):
        cart = Cart.objects.create(user_id=1)
        CartItem.objects.create(cart=cart, product_id=1, quantity=2)

        client = APIClient()
        response = client.delete("/cart/clear", format="json", **self._auth_headers())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(cart.items.count(), 0)

    def test_customer_cannot_read_other_cart(self):
        Cart.objects.create(user_id=2)

        client = APIClient()
        response = client.get("/cart/", **self._auth_headers(user_id=1))

        self.assertEqual(response.status_code, 404)
