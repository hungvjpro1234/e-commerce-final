import csv
import json
import math
import random
from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import mean

import matplotlib
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.product_client import ProductServiceClient
from app.config import get_settings
from app.models.behavior import BehaviorEvent
from app.schemas.product import ProductCatalogItem


matplotlib.use("Agg")
import matplotlib.pyplot as plt


def fetch_product_catalog(client: ProductServiceClient | None = None) -> list[ProductCatalogItem]:
    effective_client = client or ProductServiceClient()
    return effective_client.fetch_products()


def export_phase3_artifacts(
    session: Session,
    client: ProductServiceClient | None = None,
) -> dict[str, object]:
    settings = get_settings()
    products = fetch_product_catalog(client=client)
    product_map = {product.id: product for product in products}
    actual_behavior_records = _load_behavior_records(session=session, product_map=product_map)
    synthetic_records = generate_synthetic_behavior_records(products=products, target_event_count=max(180, len(products) * 15))
    sequence_records = build_sequence_records(actual_behavior_records + synthetic_records)
    split_payload = build_train_val_test_split(sequence_records)

    docs_artifacts_dir = Path(settings.docs_artifacts_dir)
    datasets_dir = docs_artifacts_dir / "datasets"
    tables_dir = docs_artifacts_dir / "tables"
    plots_dir = docs_artifacts_dir / "plots"
    reports_dir = docs_artifacts_dir / "reports"
    eval_dir = docs_artifacts_dir / "eval"
    for directory in [datasets_dir, tables_dir, plots_dir, reports_dir, eval_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    snapshot_json = datasets_dir / "phase-3-product-snapshot.json"
    snapshot_csv = datasets_dir / "phase-3-product-snapshot.csv"
    corpus_jsonl = datasets_dir / "phase-3-product-document-corpus.jsonl"
    corpus_csv = datasets_dir / "phase-3-product-document-corpus.csv"
    cleaned_json = datasets_dir / "phase-3-cleaned-behavior-dataset.json"
    cleaned_csv = datasets_dir / "phase-3-cleaned-behavior-dataset.csv"
    synthetic_json = datasets_dir / "phase-3-synthetic-behavior-dataset.json"
    synthetic_csv = datasets_dir / "phase-3-synthetic-behavior-dataset.csv"
    sequence_json = datasets_dir / "phase-3-sequence-dataset.json"
    split_json = datasets_dir / "phase-3-train-val-test-split.json"
    vocab_json = datasets_dir / "phase-3-product-id-vocab-mapping.json"

    category_mapping_csv = tables_dir / "phase-3-product-category-mapping.csv"
    detail_type_counts_csv = tables_dir / "phase-3-detail-type-counts.csv"
    category_counts_csv = tables_dir / "phase-3-category-counts.csv"
    sequence_summary_csv = tables_dir / "phase-3-sequence-length-summary.csv"
    dataset_stats_csv = tables_dir / "phase-3-dataset-statistics.csv"

    category_plot = plots_dir / "phase-3-category-distribution.png"
    detail_type_plot = plots_dir / "phase-3-detail-type-distribution.png"
    sequence_length_plot = plots_dir / "phase-3-sequence-length-distribution.png"
    timeline_plot = plots_dir / "phase-3-event-timeline-by-hour.png"
    comparison_plot = plots_dir / "phase-3-actual-vs-synthetic-events.png"
    heatmap_plot = plots_dir / "phase-3-user-category-heatmap.png"

    dataset_summary_json = eval_dir / "phase-3-dataset-summary.json"
    catalog_summary_json = eval_dir / "phase-3-catalog-summary.json"
    generation_report_md = reports_dir / "phase-3-synthetic-generation-report.md"
    analysis_report_md = reports_dir / "phase-3-dataset-analysis.md"

    _write_json(snapshot_json, [serialize_product(product) for product in products])
    _write_csv(snapshot_csv, [flatten_product(product) for product in products])

    corpus_records = build_product_corpus(products)
    _write_jsonl(corpus_jsonl, corpus_records)
    _write_csv(corpus_csv, corpus_records)

    _write_json(cleaned_json, actual_behavior_records)
    _write_csv(cleaned_csv, actual_behavior_records)
    _write_json(synthetic_json, synthetic_records)
    _write_csv(synthetic_csv, synthetic_records)
    _write_json(sequence_json, sequence_records)
    _write_json(split_json, split_payload)
    _write_json(vocab_json, build_product_vocab(products))

    _write_csv(category_mapping_csv, build_product_category_mapping(products))
    _write_count_csv(detail_type_counts_csv, "detail_type", Counter(product.detail_type for product in products))
    _write_count_csv(category_counts_csv, "category_name", Counter(product.category_data.name for product in products))
    _write_csv(sequence_summary_csv, build_sequence_summary(sequence_records))
    _write_csv(dataset_stats_csv, build_dataset_statistics(products, actual_behavior_records, synthetic_records, sequence_records))

    _plot_counter(Counter(product.category_data.name for product in products), "Product Categories", "Category", "Count", category_plot)
    _plot_counter(Counter(product.detail_type for product in products), "Product Detail Types", "Detail Type", "Count", detail_type_plot)
    _plot_sequence_lengths(sequence_records, sequence_length_plot)
    _plot_timeline_by_hour(actual_behavior_records, synthetic_records, timeline_plot)
    _plot_actual_vs_synthetic(actual_behavior_records, synthetic_records, comparison_plot)
    _plot_user_category_heatmap(actual_behavior_records + synthetic_records, heatmap_plot)

    catalog_summary = summarize_catalog(products=products, corpus_records=corpus_records)
    dataset_summary = summarize_datasets(
        actual_behavior_records=actual_behavior_records,
        synthetic_records=synthetic_records,
        sequence_records=sequence_records,
        split_payload=split_payload,
    )
    _write_json(catalog_summary_json, catalog_summary)
    _write_json(dataset_summary_json, dataset_summary)

    generation_report_md.write_text(build_synthetic_generation_report(dataset_summary), encoding="utf-8")
    analysis_report_md.write_text(build_phase3_dataset_report(catalog_summary, dataset_summary), encoding="utf-8")

    return {
        "product_count": len(products),
        "actual_behavior_events": len(actual_behavior_records),
        "synthetic_behavior_events": len(synthetic_records),
        "sequence_count": len(sequence_records),
        "snapshot_json_path": str(snapshot_json),
        "corpus_jsonl_path": str(corpus_jsonl),
        "cleaned_behavior_csv_path": str(cleaned_csv),
        "synthetic_behavior_csv_path": str(synthetic_csv),
        "dataset_report_path": str(analysis_report_md),
    }


def serialize_product(product: ProductCatalogItem) -> dict[str, object]:
    return product.model_dump()


def flatten_product(product: ProductCatalogItem) -> dict[str, object]:
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "category_id": product.category,
        "category_name": product.category_data.name,
        "detail_type": product.detail_type,
        "detail_json": json.dumps(product.detail, sort_keys=True),
    }


def build_product_corpus(products: Sequence[ProductCatalogItem]) -> list[dict[str, object]]:
    corpus_records: list[dict[str, object]] = []
    for product in products:
        detail_parts = [f"{key}: {value}" for key, value in sorted(product.detail.items())]
        text = " | ".join(
            [
                product.name,
                f"category: {product.category_data.name}",
                f"detail_type: {product.detail_type}",
                f"price: {product.price}",
                *detail_parts,
            ]
        )
        corpus_records.append(
            {
                "doc_id": f"product-{product.id}",
                "product_id": product.id,
                "category_id": product.category,
                "category_name": product.category_data.name,
                "detail_type": product.detail_type,
                "text": text,
            }
        )
    return corpus_records


def build_product_vocab(products: Sequence[ProductCatalogItem]) -> dict[str, object]:
    ordered = sorted(products, key=lambda item: item.id)
    return {
        "product_id_to_index": {str(product.id): index for index, product in enumerate(ordered)},
        "index_to_product_id": {str(index): product.id for index, product in enumerate(ordered)},
        "generated_at": datetime.now(UTC).isoformat(),
    }


def build_product_category_mapping(products: Sequence[ProductCatalogItem]) -> list[dict[str, object]]:
    return [
        {
            "product_id": product.id,
            "product_name": product.name,
            "category_id": product.category,
            "category_name": product.category_data.name,
            "detail_type": product.detail_type,
            "price": product.price,
        }
        for product in sorted(products, key=lambda item: item.id)
    ]


def _load_behavior_records(session: Session, product_map: dict[int, ProductCatalogItem]) -> list[dict[str, object]]:
    events = session.scalars(
        select(BehaviorEvent).order_by(BehaviorEvent.timestamp.asc(), BehaviorEvent.id.asc())
    ).all()

    records: list[dict[str, object]] = []
    for event in events:
        product = product_map.get(event.product_id) if event.product_id is not None else None
        records.append(
            {
                "id": event.id,
                "user_id": event.user_id,
                "product_id": event.product_id,
                "action": event.action,
                "query_text": event.query_text,
                "timestamp": event.timestamp.isoformat(),
                "category_name": product.category_data.name if product else None,
                "detail_type": product.detail_type if product else None,
                "price": product.price if product else None,
                "is_synthetic": False,
            }
        )
    return records


def generate_synthetic_behavior_records(
    products: Sequence[ProductCatalogItem],
    target_event_count: int = 180,
) -> list[dict[str, object]]:
    settings = get_settings()
    randomizer = random.Random(settings.synthetic_behavior_seed)
    actions_for_product = ["view", "click", "add_to_cart", "buy"]
    search_queries_by_detail_type = {
        "book": "clean architecture book",
        "electronics": "wireless electronics deal",
        "fashion": "black cotton hoodie",
        "home-living": "oak living room furniture",
        "beauty": "hydrating beauty serum",
        "sports": "training basketball gear",
        "toys": "robot kit for kids",
        "grocery": "organic healthy snack",
        "office": "office marker set",
        "pet-supplies": "dog feeding accessories",
    }
    products_by_detail_type: dict[str, list[ProductCatalogItem]] = defaultdict(list)
    for product in products:
        products_by_detail_type[product.detail_type].append(product)

    records: list[dict[str, object]] = []
    base_time = datetime(2026, 4, 29, 8, 0, tzinfo=UTC)
    next_id = 1
    user_count = max(24, len(products) * 2)
    current_time = base_time

    while len(records) < target_event_count:
        user_id = randomizer.randint(1000, 1000 + user_count - 1)
        chosen_detail_type = randomizer.choice(sorted(products_by_detail_type.keys()))
        product = randomizer.choice(products_by_detail_type[chosen_detail_type])

        query_text = search_queries_by_detail_type[chosen_detail_type]
        records.append(
            build_behavior_record(
                record_id=next_id,
                user_id=user_id,
                product=None,
                action="search",
                timestamp=current_time,
                query_text=query_text,
                is_synthetic=True,
            )
        )
        next_id += 1
        current_time += timedelta(minutes=randomizer.randint(1, 3))

        session_actions = ["view", "click"]
        if randomizer.random() > 0.35:
            session_actions.append("add_to_cart")
        if randomizer.random() > 0.55:
            session_actions.append("buy")

        for action in session_actions:
            if len(records) >= target_event_count:
                break
            records.append(
                build_behavior_record(
                    record_id=next_id,
                    user_id=user_id,
                    product=product,
                    action=action,
                    timestamp=current_time,
                    query_text=None,
                    is_synthetic=True,
                )
            )
            next_id += 1
            current_time += timedelta(minutes=randomizer.randint(1, 4))

    return records


def build_behavior_record(
    record_id: int,
    user_id: int,
    product: ProductCatalogItem | None,
    action: str,
    timestamp: datetime,
    query_text: str | None,
    is_synthetic: bool,
) -> dict[str, object]:
    return {
        "id": record_id,
        "user_id": user_id,
        "product_id": product.id if product else None,
        "action": action,
        "query_text": query_text,
        "timestamp": timestamp.isoformat(),
        "category_name": product.category_data.name if product else None,
        "detail_type": product.detail_type if product else None,
        "price": product.price if product else None,
        "is_synthetic": is_synthetic,
    }


def build_sequence_records(records: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[int, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        product_id = record.get("product_id")
        action = record.get("action")
        if product_id is None or action == "search":
            continue
        grouped[int(record["user_id"])].append(record)

    sequence_records: list[dict[str, object]] = []
    sequence_id = 1
    for user_id in sorted(grouped):
        ordered_records = sorted(grouped[user_id], key=lambda item: str(item["timestamp"]))
        sequence = [int(item["product_id"]) for item in ordered_records if item.get("product_id") is not None]
        if not sequence:
            continue
        sequence_records.append(
            {
                "sequence_id": sequence_id,
                "user_id": user_id,
                "sequence": sequence,
                "sequence_length": len(sequence),
                "source": "synthetic" if bool(ordered_records[0].get("is_synthetic")) else "actual",
            }
        )
        sequence_id += 1
    return sequence_records


def build_train_val_test_split(sequence_records: Sequence[dict[str, object]]) -> dict[str, object]:
    ordered = sorted(sequence_records, key=lambda item: (int(item["user_id"]), int(item["sequence_id"])))
    total = len(ordered)
    train_end = math.floor(total * 0.7)
    val_end = math.floor(total * 0.85)
    return {
        "train": [record["sequence_id"] for record in ordered[:train_end]],
        "val": [record["sequence_id"] for record in ordered[train_end:val_end]],
        "test": [record["sequence_id"] for record in ordered[val_end:]],
        "counts": {
            "train": len(ordered[:train_end]),
            "val": len(ordered[train_end:val_end]),
            "test": len(ordered[val_end:]),
        },
    }


def build_sequence_summary(sequence_records: Sequence[dict[str, object]]) -> list[dict[str, object]]:
    if not sequence_records:
        return []

    lengths = [int(record["sequence_length"]) for record in sequence_records]
    return [
        {"metric": "sequence_count", "value": len(sequence_records)},
        {"metric": "min_sequence_length", "value": min(lengths)},
        {"metric": "max_sequence_length", "value": max(lengths)},
        {"metric": "mean_sequence_length", "value": round(mean(lengths), 2)},
    ]


def build_dataset_statistics(
    products: Sequence[ProductCatalogItem],
    actual_behavior_records: Sequence[dict[str, object]],
    synthetic_records: Sequence[dict[str, object]],
    sequence_records: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    return [
        {"metric": "product_count", "value": len(products)},
        {"metric": "actual_behavior_count", "value": len(actual_behavior_records)},
        {"metric": "synthetic_behavior_count", "value": len(synthetic_records)},
        {"metric": "sequence_count", "value": len(sequence_records)},
        {"metric": "detail_type_count", "value": len({product.detail_type for product in products})},
        {"metric": "category_count", "value": len({product.category_data.name for product in products})},
    ]


def summarize_catalog(
    products: Sequence[ProductCatalogItem],
    corpus_records: Sequence[dict[str, object]],
) -> dict[str, object]:
    return {
        "product_count": len(products),
        "category_counts": dict(sorted(Counter(product.category_data.name for product in products).items())),
        "detail_type_counts": dict(sorted(Counter(product.detail_type for product in products).items())),
        "min_price": min(product.price for product in products),
        "max_price": max(product.price for product in products),
        "average_price": round(mean(product.price for product in products), 2),
        "document_count": len(corpus_records),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def summarize_datasets(
    actual_behavior_records: Sequence[dict[str, object]],
    synthetic_records: Sequence[dict[str, object]],
    sequence_records: Sequence[dict[str, object]],
    split_payload: dict[str, object],
) -> dict[str, object]:
    actual_action_counts = Counter(str(record["action"]) for record in actual_behavior_records)
    synthetic_action_counts = Counter(str(record["action"]) for record in synthetic_records)
    sequence_lengths = [int(record["sequence_length"]) for record in sequence_records]

    return {
        "actual_behavior_count": len(actual_behavior_records),
        "synthetic_behavior_count": len(synthetic_records),
        "actual_action_counts": dict(sorted(actual_action_counts.items())),
        "synthetic_action_counts": dict(sorted(synthetic_action_counts.items())),
        "sequence_count": len(sequence_records),
        "sequence_length_min": min(sequence_lengths) if sequence_lengths else 0,
        "sequence_length_max": max(sequence_lengths) if sequence_lengths else 0,
        "sequence_length_mean": round(mean(sequence_lengths), 2) if sequence_lengths else 0,
        "split_counts": split_payload.get("counts", {}),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def build_phase3_dataset_report(catalog_summary: dict[str, object], dataset_summary: dict[str, object]) -> str:
    return (
        "# Phase 3 Dataset Analysis\n\n"
        "## Catalog summary\n\n"
        f"- Product count: `{catalog_summary['product_count']}`\n"
        f"- Document count: `{catalog_summary['document_count']}`\n"
        f"- Price range: `{catalog_summary['min_price']}` to `{catalog_summary['max_price']}`\n"
        f"- Average price: `{catalog_summary['average_price']}`\n\n"
        "## Behavior dataset summary\n\n"
        f"- Actual behavior events: `{dataset_summary['actual_behavior_count']}`\n"
        f"- Synthetic behavior events: `{dataset_summary['synthetic_behavior_count']}`\n"
        f"- Sequence count: `{dataset_summary['sequence_count']}`\n"
        f"- Mean sequence length: `{dataset_summary['sequence_length_mean']}`\n\n"
        "## Artifact links\n\n"
        "- Product snapshot: [phase-3-product-snapshot.json](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/datasets/phase-3-product-snapshot.json)\n"
        "- Product corpus: [phase-3-product-document-corpus.jsonl](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/datasets/phase-3-product-document-corpus.jsonl)\n"
        "- Cleaned behavior dataset: [phase-3-cleaned-behavior-dataset.csv](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/datasets/phase-3-cleaned-behavior-dataset.csv)\n"
        "- Synthetic behavior dataset: [phase-3-synthetic-behavior-dataset.csv](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/datasets/phase-3-synthetic-behavior-dataset.csv)\n"
        "- Sequence dataset: [phase-3-sequence-dataset.json](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/datasets/phase-3-sequence-dataset.json)\n"
        "- Train/val/test split: [phase-3-train-val-test-split.json](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/datasets/phase-3-train-val-test-split.json)\n"
        "- Product vocab mapping: [phase-3-product-id-vocab-mapping.json](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/datasets/phase-3-product-id-vocab-mapping.json)\n\n"
        "## Methodology\n\n"
        "- Product catalog is fetched live from `product-service` and serialized as the source-of-truth snapshot for later graph and RAG phases.\n"
        "- Cleaned behavior data joins persisted events with product category/detail-type metadata to support downstream analytics and sequence preparation.\n"
        "- Synthetic behavior generation is deterministic and category-aware because the real dataset is still too small for LSTM training.\n"
        "- Sequence and split artifacts are created early in Phase 3 so later model work can reuse stable inputs.\n\n"
        "## Limitations and trade-offs\n\n"
        "- Synthetic behavior is useful for pipeline bring-up, but it is not a substitute for real user traffic.\n"
        "- Product corpus is plain text serialization for now; embedding/vector indexing is deferred to Phase 5.\n"
        "- Sequence split is deterministic and simple; richer stratification can be introduced in Phase 6 if evaluation demands it.\n"
    )


def build_synthetic_generation_report(dataset_summary: dict[str, object]) -> str:
    return (
        "# Phase 3 Synthetic Behavior Generation Report\n\n"
        "## Why synthetic data is needed\n\n"
        f"- Actual behavior events currently available: `{dataset_summary['actual_behavior_count']}`\n"
        f"- Synthetic behavior events generated: `{dataset_summary['synthetic_behavior_count']}`\n"
        "- The real event volume is not yet sufficient for stable sequence-model training, so Phase 3 adds a reproducible synthetic dataset.\n\n"
        "## Generation rules\n\n"
        "- Fixed random seed from `SYNTHETIC_BEHAVIOR_SEED`\n"
        "- Search query chosen by product `detail_type`\n"
        "- Follow-up actions sampled from `view`, `click`, `add_to_cart`, `buy`\n"
        "- Category/detail-type consistency preserved by selecting products from the matched detail type bucket\n\n"
        "## Summary\n\n"
        f"- Sequence count available after merge: `{dataset_summary['sequence_count']}`\n"
        f"- Mean sequence length: `{dataset_summary['sequence_length_mean']}`\n"
    )


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: Sequence[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def _write_csv(path: Path, rows: Sequence[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_count_csv(path: Path, key_name: str, counter: Counter[str]) -> None:
    rows = [{key_name: key, "count": count} for key, count in sorted(counter.items())]
    _write_csv(path, rows)


def _plot_counter(counter: Counter[str], title: str, x_label: str, y_label: str, output_path: Path) -> None:
    labels = list(counter.keys())
    values = [counter[label] for label in labels]
    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color="#3366cc")
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_sequence_lengths(sequence_records: Sequence[dict[str, object]], output_path: Path) -> None:
    lengths = [int(record["sequence_length"]) for record in sequence_records]
    plt.figure(figsize=(8, 5))
    plt.hist(lengths, bins=min(10, max(1, len(set(lengths)))), color="#cc6633", edgecolor="black")
    plt.title("Sequence Length Distribution")
    plt.xlabel("Sequence Length")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_timeline_by_hour(
    actual_behavior_records: Sequence[dict[str, object]],
    synthetic_records: Sequence[dict[str, object]],
    output_path: Path,
) -> None:
    actual_counter = Counter(datetime.fromisoformat(str(record["timestamp"])).hour for record in actual_behavior_records)
    synthetic_counter = Counter(datetime.fromisoformat(str(record["timestamp"])).hour for record in synthetic_records)
    hours = list(range(24))
    plt.figure(figsize=(10, 5))
    plt.plot(hours, [actual_counter.get(hour, 0) for hour in hours], marker="o", label="Actual")
    plt.plot(hours, [synthetic_counter.get(hour, 0) for hour in hours], marker="o", label="Synthetic")
    plt.title("Behavior Events by Hour")
    plt.xlabel("Hour of Day")
    plt.ylabel("Event Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_actual_vs_synthetic(
    actual_behavior_records: Sequence[dict[str, object]],
    synthetic_records: Sequence[dict[str, object]],
    output_path: Path,
) -> None:
    actual_counts = Counter(str(record["action"]) for record in actual_behavior_records)
    synthetic_counts = Counter(str(record["action"]) for record in synthetic_records)
    labels = sorted(set(actual_counts.keys()) | set(synthetic_counts.keys()))
    x_positions = list(range(len(labels)))
    width = 0.35
    plt.figure(figsize=(10, 5))
    plt.bar([position - width / 2 for position in x_positions], [actual_counts.get(label, 0) for label in labels], width=width, label="Actual")
    plt.bar([position + width / 2 for position in x_positions], [synthetic_counts.get(label, 0) for label in labels], width=width, label="Synthetic")
    plt.title("Actual vs Synthetic Behavior Events")
    plt.xlabel("Action")
    plt.ylabel("Count")
    plt.xticks(x_positions, labels)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_user_category_heatmap(records: Sequence[dict[str, object]], output_path: Path) -> None:
    user_ids = sorted({int(record["user_id"]) for record in records if record.get("category_name") is not None})[:12]
    categories = sorted({str(record["category_name"]) for record in records if record.get("category_name") is not None})
    if not user_ids or not categories:
        return

    matrix = []
    for user_id in user_ids:
        row = []
        for category in categories:
            row.append(sum(1 for record in records if int(record["user_id"]) == user_id and record.get("category_name") == category))
        matrix.append(row)

    plt.figure(figsize=(12, 5))
    plt.imshow(matrix, aspect="auto", cmap="Blues")
    plt.colorbar(label="Interactions")
    plt.title("User-Category Interaction Heatmap")
    plt.xticks(range(len(categories)), categories, rotation=35, ha="right")
    plt.yticks(range(len(user_ids)), [str(user_id) for user_id in user_ids])
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
