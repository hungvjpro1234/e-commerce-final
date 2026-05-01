import json
from pathlib import Path

from app.config import get_settings
from app.ml.train_lstm import (
    build_sequence_records,
    load_behavior_records,
    train_and_evaluate_lstm,
)
from app.services.lstm_service import LstmRecommendationService


def test_build_sequence_records_excludes_search_events():
    records = [
        {"id": 1, "user_id": 1, "product_id": None, "action": "search", "timestamp": "2026-04-30T09:00:00+00:00", "is_synthetic": False},
        {"id": 2, "user_id": 1, "product_id": 10, "action": "view", "timestamp": "2026-04-30T09:01:00+00:00", "is_synthetic": False},
        {"id": 3, "user_id": 1, "product_id": 11, "action": "click", "timestamp": "2026-04-30T09:02:00+00:00", "is_synthetic": False},
    ]

    sequences = build_sequence_records(records)

    assert len(sequences) == 1
    assert sequences[0].sequence == [10, 11]


def test_train_lstm_creates_runtime_and_report_artifacts(tmp_path: Path, monkeypatch):
    docs_dir = tmp_path / "docs"
    datasets_dir = docs_dir / "datasets"
    runtime_dir = tmp_path / "runtime"
    datasets_dir.mkdir(parents=True, exist_ok=True)

    products = [
        {
            "id": 1,
            "name": "Laptop Pro 14",
            "price": 1200.0,
            "stock": 5,
            "category": 1,
            "category_data": {"id": 1, "name": "Electronics"},
            "detail_type": "electronics",
            "detail": {"brand": "TechBrand"},
        },
        {
            "id": 2,
            "name": "Clean Architecture",
            "price": 40.0,
            "stock": 10,
            "category": 2,
            "category_data": {"id": 2, "name": "Books"},
            "detail_type": "book",
            "detail": {"author": "Robert C. Martin"},
        },
        {
            "id": 3,
            "name": "Classic Hoodie",
            "price": 30.0,
            "stock": 8,
            "category": 3,
            "category_data": {"id": 3, "name": "Fashion"},
            "detail_type": "fashion",
            "detail": {"color": "Black"},
        },
    ]
    actual_records = [
        {"id": 1, "user_id": 1, "product_id": 1, "action": "view", "timestamp": "2026-04-30T09:00:00+00:00", "is_synthetic": False},
        {"id": 2, "user_id": 1, "product_id": 2, "action": "click", "timestamp": "2026-04-30T09:01:00+00:00", "is_synthetic": False},
        {"id": 3, "user_id": 2, "product_id": 2, "action": "view", "timestamp": "2026-04-30T09:02:00+00:00", "is_synthetic": False},
        {"id": 4, "user_id": 2, "product_id": 3, "action": "buy", "timestamp": "2026-04-30T09:03:00+00:00", "is_synthetic": False},
    ]
    synthetic_records = [
        {"id": 100, "user_id": 1001, "product_id": 1, "action": "view", "timestamp": "2026-04-30T10:00:00+00:00", "is_synthetic": True},
        {"id": 101, "user_id": 1001, "product_id": 2, "action": "click", "timestamp": "2026-04-30T10:01:00+00:00", "is_synthetic": True},
        {"id": 102, "user_id": 1001, "product_id": 3, "action": "buy", "timestamp": "2026-04-30T10:02:00+00:00", "is_synthetic": True},
        {"id": 103, "user_id": 1002, "product_id": 2, "action": "view", "timestamp": "2026-04-30T10:03:00+00:00", "is_synthetic": True},
        {"id": 104, "user_id": 1002, "product_id": 1, "action": "click", "timestamp": "2026-04-30T10:04:00+00:00", "is_synthetic": True},
        {"id": 105, "user_id": 1002, "product_id": 3, "action": "buy", "timestamp": "2026-04-30T10:05:00+00:00", "is_synthetic": True},
    ]
    (datasets_dir / "phase-3-product-snapshot.json").write_text(json.dumps(products), encoding="utf-8")
    (datasets_dir / "phase-3-cleaned-behavior-dataset.json").write_text(json.dumps(actual_records), encoding="utf-8")
    (datasets_dir / "phase-3-synthetic-behavior-dataset.json").write_text(json.dumps(synthetic_records), encoding="utf-8")

    monkeypatch.setenv("DOCS_ARTIFACTS_DIR", str(docs_dir))
    monkeypatch.setenv("ARTIFACTS_DIR", str(runtime_dir))
    monkeypatch.setenv("LSTM_DEFAULT_EPOCHS", "4")
    get_settings.cache_clear()

    result = train_and_evaluate_lstm()

    assert Path(result["model_path"]).exists()
    assert Path(result["summary_path"]).exists()
    assert Path(result["report_path"]).exists()


def test_lstm_service_falls_back_to_popularity_when_history_too_short(tmp_path: Path, monkeypatch):
    runtime_dir = tmp_path / "runtime"
    model_dir = runtime_dir / "lstm"
    model_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "config": {"embedding_dim": 8, "hidden_dim": 16, "max_sequence_length": 3},
        "product_id_to_token": {"1": 1, "2": 2},
        "token_to_product_id": {"1": 1, "2": 2},
        "popularity_ranking": [2, 1],
        "min_history": 2,
    }
    (model_dir / "lstm_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    monkeypatch.setenv("ARTIFACTS_DIR", str(runtime_dir))
    get_settings.cache_clear()

    result = LstmRecommendationService().recommend_from_history([2], top_k=2)

    assert result.source == "popularity"
    assert result.items[0].product_id == 2
