import httpx

from app.clients.product_client import ProductServiceClient
from app.services.catalog import build_product_corpus, generate_synthetic_behavior_records


def test_product_client_parses_catalog_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/products/"
        return httpx.Response(
            200,
            json=[
                {
                    "id": 1,
                    "name": "Demo Book",
                    "price": 10.5,
                    "stock": 4,
                    "category": 1,
                    "category_data": {"id": 1, "name": "Books"},
                    "detail_type": "book",
                    "detail": {"author": "Author", "isbn": "123", "publisher": "Pub"},
                }
            ],
        )

    client = ProductServiceClient(
        base_url="http://testserver",
        transport=httpx.MockTransport(handler),
    )

    products = client.fetch_products()

    assert len(products) == 1
    assert products[0].detail_type == "book"
    assert products[0].category_data.name == "Books"


def test_corpus_and_synthetic_generation_are_deterministic():
    products = ProductServiceClient(
        base_url="http://testserver",
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                json=[
                    {
                        "id": 1,
                        "name": "Demo Book",
                        "price": 10.5,
                        "stock": 4,
                        "category": 1,
                        "category_data": {"id": 1, "name": "Books"},
                        "detail_type": "book",
                        "detail": {"author": "Author", "isbn": "123", "publisher": "Pub"},
                    },
                    {
                        "id": 2,
                        "name": "Demo Serum",
                        "price": 20.0,
                        "stock": 7,
                        "category": 2,
                        "category_data": {"id": 2, "name": "Beauty"},
                        "detail_type": "beauty",
                        "detail": {"brand": "Glow", "skin_type": "Dry", "volume_ml": 30},
                    },
                ],
            )
        ),
    ).fetch_products()

    corpus = build_product_corpus(products)
    synthetic = generate_synthetic_behavior_records(products, target_event_count=12)

    assert "detail_type: book" in corpus[0]["text"]
    assert len(synthetic) == 12
    assert synthetic[0]["action"] == "search"
    assert synthetic[0]["is_synthetic"] is True
