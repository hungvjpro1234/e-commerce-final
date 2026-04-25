from django.test import TestCase
from rest_framework.test import APIClient

from .models import User


class UserModelTests(TestCase):
    def test_user_role_default(self):
        user = User.objects.create_user(username="demo", password="secret123")
        self.assertEqual(user.role, "customer")


class UserApiTests(TestCase):
    def test_register(self):
        client = APIClient()
        response = client.post(
            "/auth/register",
            {"username": "alice", "password": "secret123", "email": "alice@example.com", "role": "customer"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

