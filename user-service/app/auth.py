from rest_framework import permissions


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


class BaseRolePermission(permissions.BasePermission):
    allowed_roles = set()

    def has_permission(self, request, view):
        return get_request_role(request) in self.allowed_roles


class IsAdmin(BaseRolePermission):
    allowed_roles = {"admin"}
