import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.clients.product_client import ProductServiceClient
from app.db import get_session_factory, init_db
from app.services.catalog import export_phase3_artifacts


def main() -> None:
    init_db()
    session = get_session_factory()()
    try:
        result = export_phase3_artifacts(session=session, client=ProductServiceClient())
    finally:
        session.close()

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
