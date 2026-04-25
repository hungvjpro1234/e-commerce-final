from django.test import TestCase
from rest_framework.test import APIClient


class PaymentApiTests(TestCase):
    def test_payment_success(self):
        client = APIClient()
        response = client.post("/payment/pay", {"order_id": 1, "amount": 10.5}, format="json")
        self.assertEqual(response.status_code, 201)

