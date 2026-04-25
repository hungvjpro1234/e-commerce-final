from unittest.mock import patch

from django.db.models import ForeignKey
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APIClient

from .models import Order, OrderItem


class OrderModelTests(TestCase):
    def test_order_table_name(self):
        self.assertEqual(Order._meta.db_table, "orders")

    def test_order_item_has_internal_foreign_key(self):
        field = OrderItem._meta.get_field("order")
        self.assertIsInstance(field, ForeignKey)


class OrderApiTests(TestCase):
    def _auth_headers(self, user_id=1, role="customer"):
        token = AccessToken()
        token["user_id"] = user_id
        token["id"] = user_id
        token["role"] = role
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_list_orders(self):
        Order.objects.create(user_id=1, total_price=20, status="Pending")
        client = APIClient()
        response = client.get("/orders/", **self._auth_headers(user_id=1))
        self.assertEqual(response.status_code, 200)

    @patch("app.views.clear_cart")
    @patch("app.views.create_shipment")
    @patch("app.views.create_payment")
    @patch("app.views.get_product")
    @patch("app.views.get_cart")
    def test_create_order_clears_cart_after_success(
        self,
        mock_get_cart,
        mock_get_product,
        mock_create_payment,
        mock_create_shipment,
        mock_clear_cart,
    ):
        mock_get_cart.return_value = {"items": [{"product_id": 1, "quantity": 2}]}
        mock_get_product.return_value = {"id": 1, "price": 10, "stock": 5}
        mock_create_payment.return_value = {"status": "Success"}
        mock_create_shipment.return_value = {"status": "Processing"}
        mock_clear_cart.return_value = {"detail": "Cart cleared."}

        client = APIClient()
        response = client.post("/orders/", {"address": "123 Main St"}, format="json", **self._auth_headers(user_id=1))

        self.assertEqual(response.status_code, 201)
        mock_clear_cart.assert_called_once()

    def test_customer_cannot_retrieve_other_users_order(self):
        order = Order.objects.create(user_id=2, total_price=20, status="Pending")

        client = APIClient()
        response = client.get(f"/orders/{order.id}/", **self._auth_headers(user_id=1))

        self.assertEqual(response.status_code, 404)

    def test_staff_can_update_order_status(self):
        order = Order.objects.create(user_id=1, total_price=20, status="Pending")

        client = APIClient()
        response = client.patch(
            f"/orders/{order.id}/",
            {"status": "Completed"},
            format="json",
            **self._auth_headers(user_id=99, role="staff"),
        )

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, "Completed")
