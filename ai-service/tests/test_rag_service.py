from pathlib import Path

from app.config import get_settings
from app.schemas.product import CategoryData, ProductCatalogItem
from app.services.rag import RagIndexer, retrieve_products


class FakeProductClient:
    def fetch_products(self) -> list[ProductCatalogItem]:
        return [
            ProductCatalogItem(
                id=1,
                name="Laptop Pro 14",
                price=1299.0,
                stock=6,
                category=1,
                category_data=CategoryData(id=1, name="Electronics"),
                detail_type="electronics",
                detail={"brand": "TechBrand", "memory": "16GB", "purpose": "work laptop"},
            ),
            ProductCatalogItem(
                id=2,
                name="Clean Architecture",
                price=42.0,
                stock=12,
                category=2,
                category_data=CategoryData(id=2, name="Books"),
                detail_type="book",
                detail={"author": "Robert C. Martin", "topic": "software architecture programming"},
            ),
            ProductCatalogItem(
                id=3,
                name="Classic Hoodie",
                price=29.0,
                stock=20,
                category=3,
                category_data=CategoryData(id=3, name="Fashion"),
                detail_type="fashion",
                detail={"color": "black", "material": "cotton"},
            ),
        ]


def test_rebuild_rag_index_creates_runtime_artifacts(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path / "runtime"))
    monkeypatch.setenv("DOCS_ARTIFACTS_DIR", str(tmp_path / "docs"))
    get_settings.cache_clear()

    result = RagIndexer().rebuild(client=FakeProductClient(), sample_queries=["laptop work", "programming book"])

    assert result.method == "tfidf-cosine"
    assert result.document_count == 3
    assert Path(result.artifact_paths["runtime_matrix"]).exists()
    assert Path(result.artifact_paths["phase5_report"]).exists()


def test_retrieve_products_returns_ranked_matches(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path / "runtime"))
    monkeypatch.setenv("DOCS_ARTIFACTS_DIR", str(tmp_path / "docs"))
    get_settings.cache_clear()

    indexer = RagIndexer()
    indexer.rebuild(client=FakeProductClient(), sample_queries=["laptop work"])

    items = retrieve_products("budget work laptop", top_k=2, client=FakeProductClient())

    assert items
    assert items[0].id == 1
    assert "laptop" in items[0].document_text.lower()
