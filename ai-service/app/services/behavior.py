import csv
import json
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.behavior import BehaviorEvent
from app.schemas.behavior import BehaviorEventCreate, BehaviorEventResponse, UserBehaviorHistoryResponse


def create_behavior_event(session: Session, payload: BehaviorEventCreate) -> BehaviorEventResponse:
    event = BehaviorEvent(
        user_id=payload.user_id,
        product_id=payload.product_id,
        action=payload.action,
        query_text=payload.query_text,
        timestamp=payload.timestamp or datetime.now(UTC),
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return BehaviorEventResponse.model_validate(event)


def list_behavior_for_user(session: Session, user_id: int) -> UserBehaviorHistoryResponse:
    events = session.scalars(
        select(BehaviorEvent)
        .where(BehaviorEvent.user_id == user_id)
        .order_by(BehaviorEvent.timestamp.asc(), BehaviorEvent.id.asc())
    ).all()

    return UserBehaviorHistoryResponse(
        user_id=user_id,
        total=len(events),
        items=[BehaviorEventResponse.model_validate(event) for event in events],
    )


def get_sample_behavior_payloads() -> list[BehaviorEventCreate]:
    return [
        BehaviorEventCreate(user_id=1, product_id=1, action="view", timestamp=datetime(2026, 4, 28, 9, 0, tzinfo=UTC)),
        BehaviorEventCreate(user_id=1, product_id=1, action="click", timestamp=datetime(2026, 4, 28, 9, 1, tzinfo=UTC)),
        BehaviorEventCreate(user_id=1, product_id=1, action="add_to_cart", timestamp=datetime(2026, 4, 28, 9, 2, tzinfo=UTC)),
        BehaviorEventCreate(user_id=1, product_id=1, action="buy", timestamp=datetime(2026, 4, 28, 9, 10, tzinfo=UTC)),
        BehaviorEventCreate(user_id=2, query_text="wireless headphones", action="search", timestamp=datetime(2026, 4, 28, 10, 0, tzinfo=UTC)),
        BehaviorEventCreate(user_id=2, product_id=2, action="view", timestamp=datetime(2026, 4, 28, 10, 1, tzinfo=UTC)),
        BehaviorEventCreate(user_id=2, product_id=2, action="click", timestamp=datetime(2026, 4, 28, 10, 2, tzinfo=UTC)),
        BehaviorEventCreate(user_id=2, product_id=2, action="add_to_cart", timestamp=datetime(2026, 4, 28, 10, 3, tzinfo=UTC)),
        BehaviorEventCreate(user_id=3, query_text="organic snacks", action="search", timestamp=datetime(2026, 4, 28, 11, 0, tzinfo=UTC)),
        BehaviorEventCreate(user_id=3, product_id=8, action="view", timestamp=datetime(2026, 4, 28, 11, 2, tzinfo=UTC)),
        BehaviorEventCreate(user_id=3, product_id=8, action="click", timestamp=datetime(2026, 4, 28, 11, 3, tzinfo=UTC)),
        BehaviorEventCreate(user_id=3, product_id=8, action="buy", timestamp=datetime(2026, 4, 28, 11, 9, tzinfo=UTC)),
    ]


def seed_sample_behavior(session: Session) -> int:
    existing_count = session.query(BehaviorEvent).count()
    if existing_count > 0:
        return existing_count

    for payload in get_sample_behavior_payloads():
        session.add(
            BehaviorEvent(
                user_id=payload.user_id,
                product_id=payload.product_id,
                action=payload.action,
                query_text=payload.query_text,
                timestamp=payload.timestamp or datetime.now(UTC),
            )
        )

    session.commit()
    return session.query(BehaviorEvent).count()


def export_behavior_artifacts(session: Session) -> dict[str, object]:
    settings = get_settings()
    docs_artifacts_dir = Path(settings.docs_artifacts_dir)
    datasets_dir = docs_artifacts_dir / "datasets"
    tables_dir = docs_artifacts_dir / "tables"
    plots_dir = docs_artifacts_dir / "plots"
    reports_dir = docs_artifacts_dir / "reports"
    eval_dir = docs_artifacts_dir / "eval"

    for directory in [datasets_dir, tables_dir, plots_dir, reports_dir, eval_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    events = session.scalars(
        select(BehaviorEvent).order_by(BehaviorEvent.timestamp.asc(), BehaviorEvent.id.asc())
    ).all()

    records = [
        {
            "id": event.id,
            "user_id": event.user_id,
            "product_id": event.product_id,
            "action": event.action,
            "query_text": event.query_text,
            "timestamp": event.timestamp.isoformat(),
        }
        for event in events
    ]

    action_counts = Counter(event.action for event in events)
    user_counts = Counter(event.user_id for event in events)
    product_counts = Counter(event.product_id for event in events if event.product_id is not None)
    date_counts = Counter(event.timestamp.date().isoformat() for event in events)

    raw_json_path = datasets_dir / "phase-2-sample-behavior-events.json"
    raw_csv_path = datasets_dir / "phase-2-sample-behavior-events.csv"
    summary_json_path = eval_dir / "phase-2-behavior-summary.json"
    action_table_path = tables_dir / "phase-2-behavior-action-counts.csv"
    user_table_path = tables_dir / "phase-2-behavior-user-counts.csv"
    product_table_path = tables_dir / "phase-2-behavior-product-counts.csv"
    chart_path = plots_dir / "phase-2-behavior-distribution.md"
    report_path = reports_dir / "phase-2-behavior-analysis.md"

    raw_json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    with raw_csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["id", "user_id", "product_id", "action", "query_text", "timestamp"])
        writer.writeheader()
        writer.writerows(records)

    summary_payload = {
        "total_events": len(records),
        "unique_users": len(user_counts),
        "unique_products": len(product_counts),
        "action_counts": dict(sorted(action_counts.items())),
        "user_counts": dict(sorted(user_counts.items())),
        "product_counts": dict(sorted(product_counts.items())),
        "date_counts": dict(sorted(date_counts.items())),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    summary_json_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    _write_count_table(action_table_path, "action", action_counts)
    _write_count_table(user_table_path, "user_id", user_counts)
    _write_count_table(product_table_path, "product_id", product_counts)

    chart_path.write_text(_build_mermaid_chart(summary_payload), encoding="utf-8")
    report_path.write_text(_build_behavior_report(summary_payload), encoding="utf-8")

    return {
        "events": len(records),
        "raw_json_path": str(raw_json_path),
        "raw_csv_path": str(raw_csv_path),
        "summary_json_path": str(summary_json_path),
        "report_path": str(report_path),
        "chart_path": str(chart_path),
    }


def _write_count_table(path: Path, key_name: str, counter: Counter[object]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([key_name, "count"])
        for key, count in sorted(counter.items(), key=lambda item: str(item[0])):
            writer.writerow([key, count])


def _build_mermaid_chart(summary_payload: dict[str, object]) -> str:
    action_counts = summary_payload["action_counts"]
    if not isinstance(action_counts, dict):
        action_counts = {}

    bars = "\n".join(
        f'    "{action}" : {count}'
        for action, count in action_counts.items()
    )

    return (
        "# Phase 2 Behavior Distribution Charts\n\n"
        "## Action distribution\n\n"
        "```mermaid\n"
        "pie showData\n"
        f"{bars}\n"
        "```\n"
    )


def _build_behavior_report(summary_payload: dict[str, object]) -> str:
    total_events = summary_payload["total_events"]
    unique_users = summary_payload["unique_users"]
    unique_products = summary_payload["unique_products"]
    action_counts = summary_payload["action_counts"]
    user_counts = summary_payload["user_counts"]
    product_counts = summary_payload["product_counts"]

    return (
        "# Phase 2 Behavior Analysis\n\n"
        "## Summary\n\n"
        f"- Total events: `{total_events}`\n"
        f"- Unique users: `{unique_users}`\n"
        f"- Unique products: `{unique_products}`\n\n"
        "## Action counts\n\n"
        "| Action | Count |\n"
        "| --- | --- |\n"
        + "".join(f"| {action} | {count} |\n" for action, count in action_counts.items())
        + "\n## User activity counts\n\n"
        "| User | Count |\n"
        "| --- | --- |\n"
        + "".join(f"| {user_id} | {count} |\n" for user_id, count in user_counts.items())
        + "\n## Product interaction counts\n\n"
        "| Product | Count |\n"
        "| --- | --- |\n"
        + "".join(f"| {product_id} | {count} |\n" for product_id, count in product_counts.items())
        + "\n## Notes\n\n"
        "- This Phase 2 dataset is deterministic sample data used to verify persistence and export flows.\n"
        "- Synthetic or larger-scale datasets are deferred to Phase 3.\n"
    )
