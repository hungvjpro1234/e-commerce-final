from django.test import TestCase
from rest_framework.test import APIClient


class ShippingApiTests(TestCase):
    def test_create_shipment(self):
        client = APIClient()
        response = client.post("/shipping/create", {"order_id": 1, "address": "123 Main St"}, format="json")
        self.assertEqual(response.status_code, 201)

