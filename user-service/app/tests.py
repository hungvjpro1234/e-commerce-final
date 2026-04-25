from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.test import APIClient

from .models import User


class UserModelTests(TestCase):
    def test_user_role_default(self):
        user = User.objects.create_user(username="demo", password="secret123")
        self.assertEqual(user.role, "customer")


class UserApiTests(TestCase):
    def _auth_headers(self, user_id=1, role="admin"):
        token = AccessToken()
        token["user_id"] = user_id
        token["id"] = user_id
        token["role"] = role
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_register(self):
        client = APIClient()
        response = client.post(
            "/auth/register",
            {"username": "alice", "password": "secret123", "email": "alice@example.com", "role": "customer"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_users_endpoint_requires_admin(self):
        client = APIClient()
        token = AccessToken()
        token["user_id"] = 1
        token["id"] = 1
        token["role"] = "customer"

        response = client.get("/users/", HTTP_AUTHORIZATION=f"Bearer {token}")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_and_update_user(self):
        client = APIClient()

        create_response = client.post(
            "/users/",
            {
                "username": "operator",
                "email": "operator@example.com",
                "password": "secret123",
                "role": "staff",
                "first_name": "Ops",
                "last_name": "One",
            },
            format="json",
            **self._auth_headers(),
        )
        self.assertEqual(create_response.status_code, 201)

        user_id = create_response.data["id"]
        update_response = client.patch(
            f"/users/{user_id}/",
            {"role": "customer", "first_name": "Updated"},
            format="json",
            **self._auth_headers(),
        )

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data["role"], "customer")
        self.assertEqual(update_response.data["first_name"], "Updated")
