import logging
import time

import requests
from django.conf import settings
from requests import Response

from .auth import build_internal_service_token


logger = logging.getLogger(__name__)


class ServiceClientError(Exception):
    pass


def _raise_for_response(response: Response, service_name):
    if response.status_code >= 400:
        raise ServiceClientError(f"{service_name} request failed with status {response.status_code}: {response.text}")


def _internal_headers(audience, correlation_id):
    return {
        "Authorization": f"Bearer {build_internal_service_token(audience)}",
        "X-Correlation-ID": correlation_id,
    }


def _send_request(
    *,
    service_name,
    method,
    url,
    headers,
    correlation_id,
    retries=1,
    json=None,
):
    attempts = max(1, retries)
    timeout_seconds = settings.SERVICE_CLIENT_TIMEOUT_SECONDS
    last_exception = None

    for attempt in range(1, attempts + 1):
        try:
            logger.info(
                "service_call.start correlation_id=%s service=%s method=%s url=%s attempt=%s",
                correlation_id,
                service_name,
                method.upper(),
                url,
                attempt,
            )
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                timeout=timeout_seconds,
            )
            _raise_for_response(response, service_name)
            logger.info(
                "service_call.success correlation_id=%s service=%s method=%s status=%s attempt=%s",
                correlation_id,
                service_name,
                method.upper(),
                response.status_code,
                attempt,
            )
            return response.json()
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_exception = exc
            logger.warning(
                "service_call.retryable_error correlation_id=%s service=%s method=%s attempt=%s error=%s",
                correlation_id,
                service_name,
                method.upper(),
                attempt,
                exc,
            )
            if attempt >= attempts:
                break
            time.sleep(0.2 * attempt)
        except requests.RequestException as exc:
            logger.error(
                "service_call.request_exception correlation_id=%s service=%s method=%s error=%s",
                correlation_id,
                service_name,
                method.upper(),
                exc,
            )
            raise ServiceClientError(f"{service_name} request failed: {exc}") from exc

    raise ServiceClientError(
        f"{service_name} request failed after {attempts} attempt(s): {last_exception}"
    ) from last_exception


def get_cart(user_id, correlation_id):
    return _send_request(
        service_name="cart-service",
        method="get",
        url=f"{settings.CART_SERVICE_URL}/internal/cart/{user_id}/",
        headers=_internal_headers("cart-service", correlation_id),
        correlation_id=correlation_id,
        retries=settings.SERVICE_CLIENT_GET_RETRIES,
    )


def clear_cart(user_id, correlation_id):
    return _send_request(
        service_name="cart-service",
        method="delete",
        url=f"{settings.CART_SERVICE_URL}/internal/cart/{user_id}/clear",
        headers=_internal_headers("cart-service", correlation_id),
        correlation_id=correlation_id,
        retries=settings.SERVICE_CLIENT_DELETE_RETRIES,
    )


def get_product(product_id, correlation_id):
    return _send_request(
        service_name="product-service",
        method="get",
        url=f"{settings.PRODUCT_SERVICE_URL}/internal/products/{product_id}/",
        headers=_internal_headers("product-service", correlation_id),
        correlation_id=correlation_id,
        retries=settings.SERVICE_CLIENT_GET_RETRIES,
    )


def create_payment(order_id, user_id, amount, correlation_id, simulate_failure=False):
    payload = {"order_id": order_id, "user_id": user_id, "amount": amount, "simulate_failure": simulate_failure}
    return _send_request(
        service_name="payment-service",
        method="post",
        url=f"{settings.PAYMENT_SERVICE_URL}/internal/payment/pay",
        json=payload,
        headers=_internal_headers("payment-service", correlation_id),
        correlation_id=correlation_id,
        retries=1,
    )


def create_shipment(order_id, user_id, address, correlation_id):
    payload = {"order_id": order_id, "user_id": user_id, "address": address}
    return _send_request(
        service_name="shipping-service",
        method="post",
        url=f"{settings.SHIPPING_SERVICE_URL}/internal/shipping/create",
        json=payload,
        headers=_internal_headers("shipping-service", correlation_id),
        correlation_id=correlation_id,
        retries=1,
    )
