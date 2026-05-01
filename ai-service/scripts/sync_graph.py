import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.clients.product_client import ProductServiceClient
from app.db import get_session_factory, init_db
from app.graph.store import Neo4jGraphStore
from app.services.graph import sync_graph


def main() -> None:
    init_db()
    session = get_session_factory()()
    try:
        with Neo4jGraphStore() as store:
            result = sync_graph(session=session, store=store, client=ProductServiceClient())
    finally:
        session.close()

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
