from dataclasses import dataclass

from app.schemas.product import CategoryData, ProductCatalogItem
from app.services.recommend import CandidateSignal, build_reason, normalize_weights


def test_normalize_weights_renormalizes_available_sources():
    weights = normalize_weights({"lstm": 0.4, "rag": 0.3})

    assert weights == {"lstm": 0.5714, "rag": 0.4286}


def test_build_reason_mentions_combined_sources():
    reason = build_reason(
        {"lstm": 0.9, "graph": 0.7},
        ["predicted from user interaction sequence", "same category"],
    )

    assert "graph + lstm" in reason or "lstm + graph" in reason
    assert "same category" in reason
