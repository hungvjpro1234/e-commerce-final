import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.clients.product_client import ProductServiceClient
from app.db import get_session_factory, init_db
from app.graph.store import Neo4jGraphStore
from app.services.graph import export_graph_artifacts


def main() -> None:
    init_db()
    session = get_session_factory()()
    try:
        with Neo4jGraphStore() as store:
            result = export_graph_artifacts(session=session, store=store, client=ProductServiceClient())
    finally:
        session.close()

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
