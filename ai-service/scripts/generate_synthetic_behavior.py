import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.clients.product_client import ProductServiceClient
from app.services.catalog import fetch_product_catalog, generate_synthetic_behavior_records


def main() -> None:
    products = fetch_product_catalog(client=ProductServiceClient())
    records = generate_synthetic_behavior_records(products=products)
    print(f"Synthetic behavior events generated: {len(records)}")


if __name__ == "__main__":
    main()
