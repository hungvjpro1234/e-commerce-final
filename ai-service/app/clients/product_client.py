from collections.abc import Sequence
import logging
import time

import httpx

from app.config import get_settings
from app.schemas.product import ProductCatalogItem


logger = logging.getLogger(__name__)


class ProductServiceClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: int | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.product_service_url).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.product_service_timeout_seconds
        self.max_retries = max(1, settings.product_service_max_retries)
        self.transport = transport

    def fetch_products(self) -> list[ProductCatalogItem]:
        last_exception = None
        with httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(
                        "product_client.fetch.start base_url=%s attempt=%s timeout=%s",
                        self.base_url,
                        attempt,
                        self.timeout_seconds,
                    )
                    response = client.get("/products/")
                    response.raise_for_status()
                    payload = response.json()
                    logger.info(
                        "product_client.fetch.success base_url=%s attempt=%s status=%s",
                        self.base_url,
                        attempt,
                        response.status_code,
                    )
                    break
                except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
                    last_exception = exc
                    logger.warning(
                        "product_client.fetch.retryable_error base_url=%s attempt=%s error=%s",
                        self.base_url,
                        attempt,
                        exc,
                    )
                    if attempt >= self.max_retries:
                        raise
                    time.sleep(0.2 * attempt)
                except httpx.HTTPStatusError:
                    raise
                except httpx.HTTPError as exc:
                    last_exception = exc
                    logger.error(
                        "product_client.fetch.http_error base_url=%s attempt=%s error=%s",
                        self.base_url,
                        attempt,
                        exc,
                    )
                    raise
            else:
                raise RuntimeError(f"Failed to fetch products from {self.base_url}: {last_exception}")

        if not isinstance(payload, Sequence):
            raise ValueError("Product service returned a non-list payload.")

        return [ProductCatalogItem.model_validate(item) for item in payload]
