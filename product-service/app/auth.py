import jwt
from django.conf import settings
from rest_framework import authentication, exceptions, permissions


class ServicePrincipal:
    def __init__(self, service_name, claims):
        self.service_name = service_name
        self.claims = claims
        self.is_authenticated = True


class InternalServiceAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise exceptions.AuthenticationFailed("Invalid authorization header.")

        try:
            claims = jwt.decode(
                parts[1],
                settings.INTERNAL_SERVICE_JWT_SECRET,
                algorithms=[settings.INTERNAL_SERVICE_JWT_ALGORITHM],
                audience=settings.INTERNAL_SERVICE_AUDIENCE,
                issuer=settings.INTERNAL_SERVICE_ISSUER,
            )
        except jwt.PyJWTError as exc:
            raise exceptions.AuthenticationFailed(f"Invalid internal service token: {exc}") from exc

        service_name = claims.get("service")
        if not service_name:
            raise exceptions.AuthenticationFailed("Missing service claim.")

        return ServicePrincipal(service_name, claims), claims


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


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return get_request_role(request) == "admin"
