import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.clients.product_client import ProductServiceClient
from app.services.catalog import fetch_product_catalog


def main() -> None:
    client = ProductServiceClient()
    products = fetch_product_catalog(client=client)
    print(f"Fetched products: {len(products)}")
    for product in products:
        print(f"{product.id}: {product.name} [{product.detail_type}]")


if __name__ == "__main__":
    main()
