import requests
from django.conf import settings

from .auth import build_internal_service_token


class ServiceClientError(Exception):
    pass


def _raise_for_response(response, service_name):
    if response.status_code >= 400:
        raise ServiceClientError(f"{service_name} request failed with status {response.status_code}: {response.text}")


def _internal_headers(audience, correlation_id):
    return {
        "Authorization": f"Bearer {build_internal_service_token(audience)}",
        "X-Correlation-ID": correlation_id,
    }


def get_cart(user_id, correlation_id):
    response = requests.get(
        f"{settings.CART_SERVICE_URL}/internal/cart/{user_id}/",
        headers=_internal_headers("cart-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "cart-service")
    return response.json()


def clear_cart(user_id, correlation_id):
    response = requests.delete(
        f"{settings.CART_SERVICE_URL}/internal/cart/{user_id}/clear",
        headers=_internal_headers("cart-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "cart-service")
    return response.json()


def get_product(product_id, correlation_id):
    response = requests.get(
        f"{settings.PRODUCT_SERVICE_URL}/internal/products/{product_id}/",
        headers=_internal_headers("product-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "product-service")
    return response.json()


def create_payment(order_id, user_id, amount, correlation_id, simulate_failure=False):
    payload = {"order_id": order_id, "user_id": user_id, "amount": amount, "simulate_failure": simulate_failure}
    response = requests.post(
        f"{settings.PAYMENT_SERVICE_URL}/internal/payment/pay",
        json=payload,
        headers=_internal_headers("payment-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "payment-service")
    return response.json()


def create_shipment(order_id, user_id, address, correlation_id):
    payload = {"order_id": order_id, "user_id": user_id, "address": address}
    response = requests.post(
        f"{settings.SHIPPING_SERVICE_URL}/internal/shipping/create",
        json=payload,
        headers=_internal_headers("shipping-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "shipping-service")
    return response.json()
