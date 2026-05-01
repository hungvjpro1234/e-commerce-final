from dataclasses import dataclass, field
from typing import Any

from app.schemas.product import CategoryData, ProductCatalogItem
from app.services.graph import compute_similarity_edges, get_graph_recommendations


@dataclass
class FakeGraphStore:
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    popular: list[dict[str, Any]] = field(default_factory=list)
    interacted_ids: list[int] = field(default_factory=list)

    def get_user_recommendations(self, user_id: int, limit: int) -> list[dict[str, Any]]:
        return self.recommendations[:limit]

    def get_user_interacted_product_ids(self, user_id: int) -> list[int]:
        return self.interacted_ids

    def get_popular_products(self, limit: int, exclude_product_ids: list[int] | None = None) -> list[dict[str, Any]]:
        return self.popular[:limit]


def test_compute_similarity_edges_builds_same_category_similarity():
    products = [
        ProductCatalogItem(
            id=1,
            name="Laptop Alpha",
            price=1000.0,
            stock=5,
            category=2,
            category_data=CategoryData(id=2, name="Electronics"),
            detail_type="electronics",
            detail={"brand": "TechBrand", "model": "A1", "warranty_months": 12},
        ),
        ProductCatalogItem(
            id=2,
            name="Laptop Beta",
            price=950.0,
            stock=6,
            category=2,
            category_data=CategoryData(id=2, name="Electronics"),
            detail_type="electronics",
            detail={"brand": "TechBrand", "model": "B2", "warranty_months": 24},
        ),
    ]

    edges = compute_similarity_edges(products)

    assert len(edges) == 1
    assert edges[0]["source_id"] == 1
    assert edges[0]["target_id"] == 2
    assert edges[0]["score"] > 0.5


def test_graph_recommendations_fallback_to_popularity():
    store = FakeGraphStore(
        recommendations=[],
        popular=[
            {
                "id": 5,
                "name": "Popular Product",
                "price": 22.0,
                "category_name": "Books",
                "detail_type": "book",
                "interaction_count": 7,
            }
        ],
        interacted_ids=[1, 2],
    )

    response = get_graph_recommendations(user_id=99, store=store, limit=5)

    assert response.total == 1
    assert response.items[0].id == 5
    assert "Fallback popularity score" in response.items[0].reason
