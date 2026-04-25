import uuid
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from rest_framework import exceptions, permissions


ROLE_ADMIN = "admin"
ROLE_STAFF = "staff"
ROLE_CUSTOMER = "customer"


class BaseRolePermission(permissions.BasePermission):
    allowed_roles = set()

    def has_permission(self, request, view):
        return get_request_role(request) in self.allowed_roles


class IsAdmin(BaseRolePermission):
    allowed_roles = {ROLE_ADMIN}


class IsStaff(BaseRolePermission):
    allowed_roles = {ROLE_STAFF}


class IsCustomer(BaseRolePermission):
    allowed_roles = {ROLE_CUSTOMER}


class IsStaffOrAdmin(BaseRolePermission):
    allowed_roles = {ROLE_ADMIN, ROLE_STAFF}


def get_token_claim(request, *keys):
    token = getattr(request, "auth", None)
    if token is None:
        return None

    for key in keys:
        value = token.get(key)
        if value is not None:
            return value
    return None


def get_request_role(request):
    return str(get_token_claim(request, "role") or "").lower()


def get_request_user_id(request):
    user_id = get_token_claim(request, "user_id", "id")
    if user_id is None:
        subject = get_token_claim(request, "sub")
        if isinstance(subject, str) and subject.isdigit():
            user_id = int(subject)

    if user_id is None:
        raise exceptions.PermissionDenied("Authenticated token is missing user identity.")
    return int(user_id)


def is_staff_or_admin(request):
    return get_request_role(request) in {ROLE_ADMIN, ROLE_STAFF}


def get_correlation_id(request):
    return request.headers.get("X-Correlation-ID") or str(uuid.uuid4())


def build_internal_service_token(audience):
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "iss": settings.INTERNAL_SERVICE_ISSUER,
        "aud": audience,
        "service": settings.INTERNAL_SERVICE_NAME,
    }
    return jwt.encode(payload, settings.INTERNAL_SERVICE_JWT_SECRET, algorithm=settings.INTERNAL_SERVICE_JWT_ALGORITHM)
