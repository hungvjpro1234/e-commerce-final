from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APIClient


class ShippingApiTests(TestCase):
    def _auth_headers(self, user_id=1, role="customer"):
        token = AccessToken()
        token["user_id"] = user_id
        token["id"] = user_id
        token["role"] = role
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_customer_cannot_read_other_shipping_status(self):
        from .models import Shipment

        Shipment.objects.create(order_id=1, user_id=2, address="123 Main St", status="Processing")

        client = APIClient()
        response = client.get("/shipping/status/1", **self._auth_headers(user_id=1))

        self.assertEqual(response.status_code, 404)
