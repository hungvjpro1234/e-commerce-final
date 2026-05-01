import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.clients.product_client import ProductServiceClient
from app.db import get_session_factory
from app.services.recommend import export_phase7_artifacts


def main() -> None:
    session = get_session_factory()()
    try:
        result = export_phase7_artifacts(session=session, client=ProductServiceClient())
    finally:
        session.close()
    print(result)


if __name__ == "__main__":
    main()
