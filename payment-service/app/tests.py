from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APIClient


class PaymentApiTests(TestCase):
    def _auth_headers(self, user_id=1, role="customer"):
        token = AccessToken()
        token["user_id"] = user_id
        token["id"] = user_id
        token["role"] = role
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_payment_status_requires_owner(self):
        from .models import Payment

        Payment.objects.create(order_id=1, user_id=2, amount=10.5, status="Success")

        client = APIClient()
        response = client.get("/payment/status/1", **self._auth_headers(user_id=1))

        self.assertEqual(response.status_code, 404)
