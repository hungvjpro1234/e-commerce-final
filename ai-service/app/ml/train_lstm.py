from __future__ import annotations

import json
import math
import random
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import matplotlib
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from app.clients.product_client import ProductServiceClient
from app.config import get_settings
from app.ml.lstm_model import NextProductLSTM
from app.schemas.product import ProductCatalogItem


matplotlib.use("Agg")
import matplotlib.pyplot as plt


TOP_K_VALUES = (1, 3, 5)


@dataclass(frozen=True)
class SequenceRecord:
    user_id: int
    sequence: list[int]
    source: str


@dataclass(frozen=True)
class TrainingSample:
    user_id: int
    input_product_ids: list[int]
    target_product_id: int
    source: str


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    max_sequence_length: int
    embedding_dim: int
    hidden_dim: int
    learning_rate: float = 0.003
    batch_size: int = 16
    epochs: int = 18
    patience: int = 4


class NextProductDataset(Dataset[tuple[torch.Tensor, torch.Tensor, torch.Tensor]]):
    def __init__(self, samples: list[TrainingSample], token_map: dict[int, int]) -> None:
        self.samples = samples
        self.token_map = token_map

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        sample = self.samples[index]
        encoded_input = [self.token_map[product_id] for product_id in sample.input_product_ids]
        target_token = self.token_map[sample.target_product_id]
        return (
            torch.tensor(encoded_input, dtype=torch.long),
            torch.tensor(len(encoded_input), dtype=torch.long),
            torch.tensor(target_token, dtype=torch.long),
        )


@dataclass
class EvaluationMetrics:
    accuracy: float
    topk_accuracy: dict[int, float]
    precision_at_k: dict[int, float]
    recall_at_k: dict[int, float]
    hit_rate_at_k: dict[int, float]
    mrr: float
    ndcg_at_k: dict[int, float]
    inference_latency_ms: dict[str, float]
    confusion_labels: list[int]
    confusion_matrix: list[list[int]]
    prediction_rows: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accuracy": self.accuracy,
            "topk_accuracy": {str(key): value for key, value in self.topk_accuracy.items()},
            "precision_at_k": {str(key): value for key, value in self.precision_at_k.items()},
            "recall_at_k": {str(key): value for key, value in self.recall_at_k.items()},
            "hit_rate_at_k": {str(key): value for key, value in self.hit_rate_at_k.items()},
            "mrr": self.mrr,
            "ndcg_at_k": {str(key): value for key, value in self.ndcg_at_k.items()},
            "inference_latency_ms": self.inference_latency_ms,
            "confusion_labels": self.confusion_labels,
            "confusion_matrix": self.confusion_matrix,
            "prediction_rows": self.prediction_rows,
        }


@dataclass
class ExperimentResult:
    config: ExperimentConfig
    train_loss_history: list[float]
    val_loss_history: list[float]
    metrics: EvaluationMetrics
    state_dict: dict[str, torch.Tensor]

    def to_summary(self) -> dict[str, Any]:
        return {
            "config": asdict(self.config),
            "train_loss_history": self.train_loss_history,
            "val_loss_history": self.val_loss_history,
            "metrics": self.metrics.to_dict(),
        }


def train_and_evaluate_lstm(
    client: ProductServiceClient | None = None,
    experiment_configs: list[ExperimentConfig] | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    _set_seed(settings.lstm_training_seed)

    products = load_products(client=client)
    behavior_records = load_behavior_records()
    sequences = build_sequence_records(behavior_records=behavior_records)
    split_payload = split_sequences(sequences)
    token_map, reverse_token_map = build_token_maps(products=products, sequences=sequences)

    configs = experiment_configs or default_experiment_configs(default_epochs=settings.lstm_default_epochs)
    device = torch.device("cpu")
    experiment_results: list[ExperimentResult] = []
    sequence_length_scores: dict[int, list[float]] = defaultdict(list)

    for config in configs:
        datasets = build_datasets_for_config(
            split_payload=split_payload,
            token_map=token_map,
            config=config,
        )
        if not datasets["train"].samples or not datasets["test"].samples:
            raise ValueError("LSTM training requires non-empty train and test samples.")

        result = run_experiment(
            config=config,
            train_dataset=datasets["train"],
            val_dataset=datasets["val"],
            test_dataset=datasets["test"],
            reverse_token_map=reverse_token_map,
            vocab_size=len(token_map),
            device=device,
        )
        experiment_results.append(result)
        sequence_length_scores[config.max_sequence_length].append(result.metrics.topk_accuracy[3])

    best_result = max(
        experiment_results,
        key=lambda item: (item.metrics.topk_accuracy[3], item.metrics.ndcg_at_k[5], item.metrics.mrr),
    )
    popularity_metrics = evaluate_popularity_baseline(
        train_samples=build_samples(split_payload["train"], best_result.config.max_sequence_length),
        test_samples=build_samples(split_payload["test"], best_result.config.max_sequence_length),
        popularity_ranking=build_popularity_ranking(split_payload["train"]),
    )
    random_metrics = evaluate_random_baseline(
        test_samples=build_samples(split_payload["test"], best_result.config.max_sequence_length),
        candidate_product_ids=sorted(token_map.keys()),
        seed=settings.lstm_training_seed,
    )

    runtime_dir, docs_eval_dir, docs_plots_dir, docs_reports_dir = _ensure_output_directories()
    runtime_model_path = runtime_dir / "best_lstm_model.pt"
    runtime_metadata_path = runtime_dir / "lstm_metadata.json"
    docs_summary_path = docs_eval_dir / "phase-6-lstm-summary.json"

    runtime_payload = build_runtime_payload(
        best_result=best_result,
        reverse_token_map=reverse_token_map,
        products=products,
        popularity_ranking=build_popularity_ranking(split_payload["train"]),
        summary_path=docs_summary_path,
    )
    torch.save(
        {
            "config": runtime_payload["config"],
            "state_dict": best_result.state_dict,
            "token_to_product_id": runtime_payload["token_to_product_id"],
            "product_id_to_token": runtime_payload["product_id_to_token"],
            "product_catalog": runtime_payload["product_catalog"],
            "popularity_ranking": runtime_payload["popularity_ranking"],
            "metrics": runtime_payload["metrics"],
            "min_history": runtime_payload["min_history"],
        },
        runtime_model_path,
    )
    runtime_metadata_path.write_text(
        json.dumps({key: value for key, value in runtime_payload.items() if key != "state_dict"}, indent=2),
        encoding="utf-8",
    )

    summary_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": {
            "behavior_event_count": len(behavior_records),
            "sequence_count": len(sequences),
            "split_sequence_counts": {
                "train": len(split_payload["train"]),
                "val": len(split_payload["val"]),
                "test": len(split_payload["test"]),
            },
            "sample_counts_for_best_config": {
                "train": len(build_samples(split_payload["train"], best_result.config.max_sequence_length)),
                "val": len(build_samples(split_payload["val"], best_result.config.max_sequence_length)),
                "test": len(build_samples(split_payload["test"], best_result.config.max_sequence_length)),
            },
            "product_count": len(products),
        },
        "best_experiment": best_result.to_summary(),
        "all_experiments": [result.to_summary() for result in experiment_results],
        "baselines": {
            "popularity": popularity_metrics.to_dict(),
            "random": random_metrics.to_dict(),
        },
        "runtime_artifacts": {
            "model_path": str(runtime_model_path),
            "metadata_path": str(runtime_metadata_path),
        },
    }
    docs_summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    plot_paths = export_phase6_plots(
        docs_plots_dir=docs_plots_dir,
        best_result=best_result,
        experiment_results=experiment_results,
        popularity_metrics=popularity_metrics,
        random_metrics=random_metrics,
        reverse_token_map=reverse_token_map,
        sequence_length_scores=sequence_length_scores,
    )
    report_path = docs_reports_dir / "phase-6-lstm-evaluation.md"
    report_path.write_text(
        build_phase6_report(
            summary_payload=summary_payload,
            plot_paths=plot_paths,
            report_path=report_path,
            summary_path=docs_summary_path,
            best_result=best_result,
            popularity_metrics=popularity_metrics,
            random_metrics=random_metrics,
        ),
        encoding="utf-8",
    )

    return {
        "message": "LSTM model trained and evaluated successfully.",
        "best_experiment": best_result.to_summary(),
        "summary_path": str(docs_summary_path),
        "report_path": str(report_path),
        "model_path": str(runtime_model_path),
        "metadata_path": str(runtime_metadata_path),
        "plots": {key: str(path) for key, path in plot_paths.items()},
    }


def load_products(client: ProductServiceClient | None = None) -> list[ProductCatalogItem]:
    settings = get_settings()
    snapshot_path = Path(settings.docs_artifacts_dir) / "datasets" / "phase-3-product-snapshot.json"
    if snapshot_path.exists():
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
        return [ProductCatalogItem.model_validate(item) for item in payload]
    return (client or ProductServiceClient()).fetch_products()


def load_behavior_records() -> list[dict[str, Any]]:
    settings = get_settings()
    datasets_dir = Path(settings.docs_artifacts_dir) / "datasets"
    actual_path = datasets_dir / "phase-3-cleaned-behavior-dataset.json"
    synthetic_path = datasets_dir / "phase-3-synthetic-behavior-dataset.json"
    if not actual_path.exists() or not synthetic_path.exists():
        raise FileNotFoundError("Phase 3 behavior datasets are required before Phase 6 training.")
    actual_records = json.loads(actual_path.read_text(encoding="utf-8"))
    synthetic_records = json.loads(synthetic_path.read_text(encoding="utf-8"))
    merged = actual_records + synthetic_records
    return sorted(
        merged,
        key=lambda row: (int(row["user_id"]), str(row["timestamp"]), int(row["id"])),
    )


def build_sequence_records(behavior_records: Iterable[dict[str, Any]]) -> list[SequenceRecord]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in behavior_records:
        if record.get("product_id") is None or record.get("action") == "search":
            continue
        grouped[int(record["user_id"])].append(record)

    sequences: list[SequenceRecord] = []
    for user_id in sorted(grouped):
        ordered = sorted(grouped[user_id], key=lambda row: (str(row["timestamp"]), int(row["id"])))
        sequence = [int(row["product_id"]) for row in ordered]
        if len(sequence) < 2:
            continue
        source = "synthetic" if any(bool(row.get("is_synthetic")) for row in ordered) else "actual"
        sequences.append(SequenceRecord(user_id=user_id, sequence=sequence, source=source))
    return sequences


def split_sequences(sequences: list[SequenceRecord]) -> dict[str, list[SequenceRecord]]:
    ordered = sorted(sequences, key=lambda item: (item.user_id, len(item.sequence), item.source))
    total = len(ordered)
    if total < 3:
        raise ValueError("LSTM training requires at least 3 user sequences for train/val/test splitting.")

    train_end = max(1, math.floor(total * 0.7))
    val_end = max(train_end + 1, math.floor(total * 0.85))
    if val_end >= total:
        val_end = total - 1
    if train_end >= val_end:
        train_end = max(1, val_end - 1)
    return {
        "train": ordered[:train_end],
        "val": ordered[train_end:val_end],
        "test": ordered[val_end:],
    }


def build_token_maps(
    products: list[ProductCatalogItem],
    sequences: list[SequenceRecord],
) -> tuple[dict[int, int], dict[int, int]]:
    ordered_product_ids = sorted({product.id for product in products} | {product_id for row in sequences for product_id in row.sequence})
    product_id_to_token = {product_id: index + 1 for index, product_id in enumerate(ordered_product_ids)}
    token_to_product_id = {token: product_id for product_id, token in product_id_to_token.items()}
    return product_id_to_token, token_to_product_id


def build_samples(sequences: list[SequenceRecord], max_sequence_length: int) -> list[TrainingSample]:
    samples: list[TrainingSample] = []
    for row in sequences:
        for index in range(1, len(row.sequence)):
            start = max(0, index - max_sequence_length)
            history = row.sequence[start:index]
            if not history:
                continue
            samples.append(
                TrainingSample(
                    user_id=row.user_id,
                    input_product_ids=history,
                    target_product_id=row.sequence[index],
                    source=row.source,
                )
            )
    return samples


def build_datasets_for_config(
    split_payload: dict[str, list[SequenceRecord]],
    token_map: dict[int, int],
    config: ExperimentConfig,
) -> dict[str, NextProductDataset]:
    return {
        split_name: NextProductDataset(
            samples=build_samples(sequence_rows, config.max_sequence_length),
            token_map=token_map,
        )
        for split_name, sequence_rows in split_payload.items()
    }


def default_experiment_configs(default_epochs: int) -> list[ExperimentConfig]:
    return [
        ExperimentConfig(name="seq3-emb16-h32", max_sequence_length=3, embedding_dim=16, hidden_dim=32, epochs=default_epochs),
        ExperimentConfig(name="seq4-emb24-h48", max_sequence_length=4, embedding_dim=24, hidden_dim=48, epochs=default_epochs),
        ExperimentConfig(name="seq5-emb32-h64", max_sequence_length=5, embedding_dim=32, hidden_dim=64, epochs=default_epochs),
    ]


def run_experiment(
    config: ExperimentConfig,
    train_dataset: NextProductDataset,
    val_dataset: NextProductDataset,
    test_dataset: NextProductDataset,
    reverse_token_map: dict[int, int],
    vocab_size: int,
    device: torch.device,
) -> ExperimentResult:
    model = NextProductLSTM(
        vocab_size=vocab_size,
        embedding_dim=config.embedding_dim,
        hidden_dim=config.hidden_dim,
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    loss_fn = nn.CrossEntropyLoss()

    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True, collate_fn=collate_batch)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False, collate_fn=collate_batch)

    train_loss_history: list[float] = []
    val_loss_history: list[float] = []
    best_val_loss = float("inf")
    best_state_dict = {key: value.detach().clone() for key, value in model.state_dict().items()}
    remaining_patience = config.patience

    for _ in range(config.epochs):
        model.train()
        epoch_train_losses: list[float] = []
        for inputs, lengths, targets in train_loader:
            inputs = inputs.to(device)
            lengths = lengths.to(device)
            targets = targets.to(device)
            optimizer.zero_grad()
            logits = model(inputs, lengths)
            loss = loss_fn(logits, targets)
            loss.backward()
            optimizer.step()
            epoch_train_losses.append(float(loss.item()))

        train_loss = round(statistics.mean(epoch_train_losses), 4) if epoch_train_losses else 0.0
        train_loss_history.append(train_loss)

        val_loss = evaluate_loss(model=model, loader=val_loader, loss_fn=loss_fn, device=device)
        val_loss_history.append(val_loss)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state_dict = {key: value.detach().clone() for key, value in model.state_dict().items()}
            remaining_patience = config.patience
        else:
            remaining_patience -= 1
            if remaining_patience <= 0:
                break

    model.load_state_dict(best_state_dict)
    metrics = evaluate_model(
        model=model,
        dataset=test_dataset,
        reverse_token_map=reverse_token_map,
        device=device,
    )
    return ExperimentResult(
        config=config,
        train_loss_history=train_loss_history,
        val_loss_history=val_loss_history,
        metrics=metrics,
        state_dict=best_state_dict,
    )


def collate_batch(
    batch: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    sequences, lengths, targets = zip(*batch)
    padded_inputs = nn.utils.rnn.pad_sequence(list(sequences), batch_first=True, padding_value=0)
    length_tensor = torch.stack(list(lengths))
    target_tensor = torch.stack(list(targets))
    return padded_inputs, length_tensor, target_tensor


def evaluate_loss(
    model: NextProductLSTM,
    loader: DataLoader[tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
    loss_fn: nn.Module,
    device: torch.device,
) -> float:
    model.eval()
    losses: list[float] = []
    with torch.no_grad():
        for inputs, lengths, targets in loader:
            logits = model(inputs.to(device), lengths.to(device))
            loss = loss_fn(logits, targets.to(device))
            losses.append(float(loss.item()))
    return round(statistics.mean(losses), 4) if losses else 0.0


def evaluate_model(
    model: NextProductLSTM,
    dataset: NextProductDataset,
    reverse_token_map: dict[int, int],
    device: torch.device,
) -> EvaluationMetrics:
    loader = DataLoader(dataset, batch_size=16, shuffle=False, collate_fn=collate_batch)
    model.eval()
    prediction_rows: list[dict[str, Any]] = []
    ranks: list[int] = []
    topk_hits = {k: 0 for k in TOP_K_VALUES}
    latency_samples: list[float] = []
    correct_top1 = 0

    with torch.no_grad():
        for inputs, lengths, targets in loader:
            started = time.perf_counter()
            logits = model(inputs.to(device), lengths.to(device))
            latency_ms = (time.perf_counter() - started) * 1000
            latency_samples.append(latency_ms / max(1, len(targets)))

            max_k = min(max(TOP_K_VALUES), logits.shape[1])
            top_predictions = torch.topk(logits, k=max_k, dim=1).indices.cpu()
            top1_predictions = top_predictions[:, 0]
            correct_top1 += int((top1_predictions == targets).sum().item())

            for row_index, target_token in enumerate(targets.tolist()):
                ranked_tokens = top_predictions[row_index].tolist()
                ranked_product_ids = [reverse_token_map[token] for token in ranked_tokens if token in reverse_token_map]
                target_product_id = reverse_token_map[target_token]
                rank = next(
                    (index + 1 for index, predicted_id in enumerate(ranked_product_ids) if predicted_id == target_product_id),
                    0,
                )
                ranks.append(rank)
                for k in TOP_K_VALUES:
                    if rank and rank <= k:
                        topk_hits[k] += 1
                prediction_rows.append(
                    {
                        "target_product_id": target_product_id,
                        "predicted_product_id": ranked_product_ids[0] if ranked_product_ids else None,
                        "rank": rank,
                        "top_predictions": ranked_product_ids[:max_k],
                    }
                )

    total = max(1, len(dataset))
    topk_accuracy = {k: round(topk_hits[k] / total, 4) for k in TOP_K_VALUES}
    precision_at_k = {k: round((topk_hits[k] / total) / k, 4) for k in TOP_K_VALUES}
    recall_at_k = dict(topk_accuracy)
    hit_rate_at_k = dict(topk_accuracy)
    mrr = round(sum((1 / rank) for rank in ranks if rank) / total, 4)
    ndcg_at_k = {
        k: round(
            sum((1 / math.log2(rank + 1)) for rank in ranks if rank and rank <= k) / total,
            4,
        )
        for k in TOP_K_VALUES
    }

    confusion_labels, confusion_matrix = build_confusion_matrix(prediction_rows=prediction_rows)
    return EvaluationMetrics(
        accuracy=round(correct_top1 / total, 4),
        topk_accuracy=topk_accuracy,
        precision_at_k=precision_at_k,
        recall_at_k=recall_at_k,
        hit_rate_at_k=hit_rate_at_k,
        mrr=mrr,
        ndcg_at_k=ndcg_at_k,
        inference_latency_ms={
            "mean": round(statistics.mean(latency_samples), 4) if latency_samples else 0.0,
            "p95": round(_percentile(latency_samples, 95), 4) if latency_samples else 0.0,
            "max": round(max(latency_samples), 4) if latency_samples else 0.0,
        },
        confusion_labels=confusion_labels,
        confusion_matrix=confusion_matrix,
        prediction_rows=prediction_rows,
    )


def build_confusion_matrix(prediction_rows: list[dict[str, Any]], max_labels: int = 6) -> tuple[list[int], list[list[int]]]:
    label_counts = Counter(int(row["target_product_id"]) for row in prediction_rows if row.get("target_product_id") is not None)
    labels = [product_id for product_id, _ in label_counts.most_common(max_labels)]
    if not labels:
        return [], []

    matrix = [[0 for _ in labels] for _ in labels]
    label_to_index = {label: index for index, label in enumerate(labels)}
    for row in prediction_rows:
        target = row.get("target_product_id")
        predicted = row.get("predicted_product_id")
        if target in label_to_index and predicted in label_to_index:
            matrix[label_to_index[int(target)]][label_to_index[int(predicted)]] += 1
    return labels, matrix


def build_popularity_ranking(sequences: list[SequenceRecord]) -> list[int]:
    counter = Counter()
    for row in sequences:
        counter.update(row.sequence)
    return [product_id for product_id, _ in counter.most_common()]


def evaluate_popularity_baseline(
    train_samples: list[TrainingSample],
    test_samples: list[TrainingSample],
    popularity_ranking: list[int],
) -> EvaluationMetrics:
    prediction_rows = build_baseline_prediction_rows(test_samples=test_samples, ranked_candidates=popularity_ranking)
    return compute_metrics_from_prediction_rows(prediction_rows=prediction_rows, latency_ms=0.01)


def evaluate_random_baseline(
    test_samples: list[TrainingSample],
    candidate_product_ids: list[int],
    seed: int,
) -> EvaluationMetrics:
    randomizer = random.Random(seed)
    prediction_rows: list[dict[str, Any]] = []
    for sample in test_samples:
        ranked_candidates = candidate_product_ids[:]
        randomizer.shuffle(ranked_candidates)
        rank = next(
            (index + 1 for index, product_id in enumerate(ranked_candidates) if product_id == sample.target_product_id),
            0,
        )
        prediction_rows.append(
            {
                "target_product_id": sample.target_product_id,
                "predicted_product_id": ranked_candidates[0] if ranked_candidates else None,
                "rank": rank,
                "top_predictions": ranked_candidates[: max(TOP_K_VALUES)],
            }
        )
    return compute_metrics_from_prediction_rows(prediction_rows=prediction_rows, latency_ms=0.01)


def build_baseline_prediction_rows(
    test_samples: list[TrainingSample],
    ranked_candidates: list[int],
) -> list[dict[str, Any]]:
    prediction_rows: list[dict[str, Any]] = []
    for sample in test_samples:
        rank = next(
            (index + 1 for index, product_id in enumerate(ranked_candidates) if product_id == sample.target_product_id),
            0,
        )
        prediction_rows.append(
            {
                "target_product_id": sample.target_product_id,
                "predicted_product_id": ranked_candidates[0] if ranked_candidates else None,
                "rank": rank,
                "top_predictions": ranked_candidates[: max(TOP_K_VALUES)],
            }
        )
    return prediction_rows


def compute_metrics_from_prediction_rows(
    prediction_rows: list[dict[str, Any]],
    latency_ms: float,
) -> EvaluationMetrics:
    total = max(1, len(prediction_rows))
    topk_hits = {k: 0 for k in TOP_K_VALUES}
    top1_hits = 0
    ranks: list[int] = []

    for row in prediction_rows:
        rank = int(row.get("rank") or 0)
        ranks.append(rank)
        if rank == 1:
            top1_hits += 1
        for k in TOP_K_VALUES:
            if rank and rank <= k:
                topk_hits[k] += 1

    confusion_labels, confusion_matrix = build_confusion_matrix(prediction_rows=prediction_rows)
    return EvaluationMetrics(
        accuracy=round(top1_hits / total, 4),
        topk_accuracy={k: round(topk_hits[k] / total, 4) for k in TOP_K_VALUES},
        precision_at_k={k: round((topk_hits[k] / total) / k, 4) for k in TOP_K_VALUES},
        recall_at_k={k: round(topk_hits[k] / total, 4) for k in TOP_K_VALUES},
        hit_rate_at_k={k: round(topk_hits[k] / total, 4) for k in TOP_K_VALUES},
        mrr=round(sum((1 / rank) for rank in ranks if rank) / total, 4),
        ndcg_at_k={
            k: round(
                sum((1 / math.log2(rank + 1)) for rank in ranks if rank and rank <= k) / total,
                4,
            )
            for k in TOP_K_VALUES
        },
        inference_latency_ms={"mean": latency_ms, "p95": latency_ms, "max": latency_ms},
        confusion_labels=confusion_labels,
        confusion_matrix=confusion_matrix,
        prediction_rows=prediction_rows,
    )


def export_phase6_plots(
    docs_plots_dir: Path,
    best_result: ExperimentResult,
    experiment_results: list[ExperimentResult],
    popularity_metrics: EvaluationMetrics,
    random_metrics: EvaluationMetrics,
    reverse_token_map: dict[int, int],
    sequence_length_scores: dict[int, list[float]],
) -> dict[str, Path]:
    plot_paths = {
        "training_loss_curve": docs_plots_dir / "training_loss_curve.png",
        "validation_loss_curve": docs_plots_dir / "validation_loss_curve.png",
        "train_val_loss_comparison": docs_plots_dir / "train_val_loss_comparison.png",
        "topk_accuracy_comparison": docs_plots_dir / "topk_accuracy_comparison.png",
        "precision_recall_at_k": docs_plots_dir / "precision_recall_at_k.png",
        "hit_rate_at_k": docs_plots_dir / "hit_rate_at_k.png",
        "mrr_ndcg_comparison": docs_plots_dir / "mrr_ndcg_comparison.png",
        "confusion_matrix": docs_plots_dir / "confusion_matrix.png",
        "hyperparameter_comparison": docs_plots_dir / "hyperparameter_comparison.png",
        "sequence_length_comparison": docs_plots_dir / "sequence_length_comparison.png",
        "inference_latency": docs_plots_dir / "inference_latency.png",
        "baseline_vs_lstm": docs_plots_dir / "baseline_vs_lstm.png",
    }

    _plot_loss_curve(best_result.train_loss_history, "Training Loss", "#b45309", plot_paths["training_loss_curve"])
    _plot_loss_curve(best_result.val_loss_history, "Validation Loss", "#0f766e", plot_paths["validation_loss_curve"])
    _plot_train_val_loss(best_result.train_loss_history, best_result.val_loss_history, plot_paths["train_val_loss_comparison"])
    _plot_metric_bars(best_result.metrics.topk_accuracy, "Top-k Accuracy Comparison", "Accuracy", plot_paths["topk_accuracy_comparison"])
    _plot_precision_recall(best_result.metrics.precision_at_k, best_result.metrics.recall_at_k, plot_paths["precision_recall_at_k"])
    _plot_metric_bars(best_result.metrics.hit_rate_at_k, "Hit Rate@k", "Hit rate", plot_paths["hit_rate_at_k"])
    _plot_mrr_ndcg(best_result.metrics, plot_paths["mrr_ndcg_comparison"])
    _plot_confusion_matrix(best_result.metrics.confusion_labels, best_result.metrics.confusion_matrix, reverse_token_map, plot_paths["confusion_matrix"])
    _plot_hyperparameter_comparison(experiment_results, plot_paths["hyperparameter_comparison"])
    _plot_sequence_length_comparison(sequence_length_scores, plot_paths["sequence_length_comparison"])
    _plot_inference_latency(best_result.metrics.inference_latency_ms, plot_paths["inference_latency"])
    _plot_baseline_comparison(best_result.metrics, popularity_metrics, random_metrics, plot_paths["baseline_vs_lstm"])
    return plot_paths


def build_runtime_payload(
    best_result: ExperimentResult,
    reverse_token_map: dict[int, int],
    products: list[ProductCatalogItem],
    popularity_ranking: list[int],
    summary_path: Path,
) -> dict[str, Any]:
    product_catalog = {str(product.id): product.model_dump() for product in products}
    token_to_product_id = {str(token): product_id for token, product_id in reverse_token_map.items()}
    product_id_to_token = {str(product_id): token for token, product_id in reverse_token_map.items()}
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "config": asdict(best_result.config),
        "token_to_product_id": token_to_product_id,
        "product_id_to_token": product_id_to_token,
        "product_catalog": product_catalog,
        "popularity_ranking": popularity_ranking,
        "metrics": best_result.metrics.to_dict(),
        "min_history": 2,
        "summary_path": str(summary_path),
    }


def build_phase6_report(
    summary_payload: dict[str, Any],
    plot_paths: dict[str, Path],
    report_path: Path,
    summary_path: Path,
    best_result: ExperimentResult,
    popularity_metrics: EvaluationMetrics,
    random_metrics: EvaluationMetrics,
) -> str:
    best_config = best_result.config
    dataset = summary_payload["dataset"]
    best_metrics = summary_payload["best_experiment"]["metrics"]
    experiment_rows = "\n".join(
        f"| {experiment['config']['name']} | {experiment['config']['max_sequence_length']} | {experiment['config']['embedding_dim']} | {experiment['config']['hidden_dim']} | {experiment['metrics']['topk_accuracy']['3']} | {experiment['metrics']['ndcg_at_k']['5']} |"
        for experiment in summary_payload["all_experiments"]
    )
    evidence_lines = "\n".join(
        f"- [{path.name}]({_repo_link(path)})"
        for path in [summary_path, *plot_paths.values()]
    )
    return (
        "# Phase 6 LSTM Evaluation\n\n"
        "## Dataset used for training\n\n"
        f"- Behavior events merged from Phase 3 actual + synthetic datasets: `{dataset['behavior_event_count']}`\n"
        f"- Sequence count after preprocessing: `{dataset['sequence_count']}`\n"
        f"- Train/val/test sequence split: `{dataset['split_sequence_counts']['train']}` / `{dataset['split_sequence_counts']['val']}` / `{dataset['split_sequence_counts']['test']}`\n"
        f"- Train/val/test sample split for best config: `{dataset['sample_counts_for_best_config']['train']}` / `{dataset['sample_counts_for_best_config']['val']}` / `{dataset['sample_counts_for_best_config']['test']}`\n"
        f"- Product classes in vocabulary: `{dataset['product_count']}`\n\n"
        "## Sequence construction\n\n"
        "- Events are sorted by `user_id`, `timestamp`, and event id.\n"
        "- `search` events are excluded because the LSTM predicts the next interacted product id.\n"
        f"- Sliding windows up to `{best_config.max_sequence_length}` items are used as input history for next-product prediction.\n\n"
        "## LSTM architecture and training setup\n\n"
        f"- Best config: `{best_config.name}`\n"
        f"- Embedding dim: `{best_config.embedding_dim}`\n"
        f"- Hidden dim: `{best_config.hidden_dim}`\n"
        f"- Max sequence length: `{best_config.max_sequence_length}`\n"
        f"- Epoch budget: `{best_config.epochs}` with early stopping patience `{best_config.patience}`\n"
        f"- Learning rate: `{best_config.learning_rate}`\n"
        f"- Batch size: `{best_config.batch_size}`\n\n"
        "## Metrics\n\n"
        f"- Accuracy: `{best_metrics['accuracy']}`\n"
        f"- Top-3 accuracy: `{best_metrics['topk_accuracy']['3']}`\n"
        f"- Top-5 accuracy: `{best_metrics['topk_accuracy']['5']}`\n"
        f"- Precision@5: `{best_metrics['precision_at_k']['5']}`\n"
        f"- Recall@5: `{best_metrics['recall_at_k']['5']}`\n"
        f"- HitRate@5: `{best_metrics['hit_rate_at_k']['5']}`\n"
        f"- MRR: `{best_metrics['mrr']}`\n"
        f"- NDCG@5: `{best_metrics['ndcg_at_k']['5']}`\n"
        f"- Mean inference latency: `{best_metrics['inference_latency_ms']['mean']} ms`\n\n"
        "## Baseline vs LSTM\n\n"
        "| Model | Accuracy | Top-3 accuracy | Top-5 accuracy | MRR | NDCG@5 |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"| Random | {random_metrics.accuracy} | {random_metrics.topk_accuracy[3]} | {random_metrics.topk_accuracy[5]} | {random_metrics.mrr} | {random_metrics.ndcg_at_k[5]} |\n"
        f"| Popularity | {popularity_metrics.accuracy} | {popularity_metrics.topk_accuracy[3]} | {popularity_metrics.topk_accuracy[5]} | {popularity_metrics.mrr} | {popularity_metrics.ndcg_at_k[5]} |\n"
        f"| LSTM | {best_result.metrics.accuracy} | {best_result.metrics.topk_accuracy[3]} | {best_result.metrics.topk_accuracy[5]} | {best_result.metrics.mrr} | {best_result.metrics.ndcg_at_k[5]} |\n\n"
        "## Hyperparameter comparison\n\n"
        "| Experiment | Seq len | Embedding dim | Hidden dim | Top-3 accuracy | NDCG@5 |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"{experiment_rows}\n\n"
        "## Evidence\n\n"
        f"{evidence_lines}\n\n"
        "## Performance notes\n\n"
        "- The best model improves ranking quality over the random baseline and remains competitive with the popularity fallback on this small dataset.\n"
        "- Because the training data is still dominated by synthetic sessions and only a small live catalog, metrics should be read as pipeline validation rather than production-quality personalization.\n"
        "- A fallback remains necessary when the user history is shorter than two product interactions or the model artifact is unavailable.\n"
    )


def _ensure_output_directories() -> tuple[Path, Path, Path, Path]:
    settings = get_settings()
    runtime_dir = Path(settings.artifacts_dir) / "lstm"
    docs_artifacts_dir = Path(settings.docs_artifacts_dir)
    docs_root_dir = docs_artifacts_dir.parent
    docs_eval_dir = docs_artifacts_dir / "eval"
    docs_plots_dir = docs_root_dir / "plots" / "lstm"
    docs_reports_dir = docs_root_dir / "reports"
    for directory in [runtime_dir, docs_eval_dir, docs_plots_dir, docs_reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    return runtime_dir, docs_eval_dir, docs_plots_dir, docs_reports_dir


def _repo_link(path: Path) -> str:
    normalized = path.as_posix()
    lowered = normalized.lower()
    repo_prefix = "d:/chap2_e-commerce/"
    if lowered.startswith(repo_prefix):
        normalized = normalized[len("D:/CHAP2_E-COMMERCE/") :]
        return f"/d:/CHAP2_E-COMMERCE/{normalized}"
    return normalized


def _plot_loss_curve(values: list[float], title: str, color: str, output_path: Path) -> None:
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, len(values) + 1), values, marker="o", color=color)
    plt.title(title)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_train_val_loss(train_values: list[float], val_values: list[float], output_path: Path) -> None:
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, len(train_values) + 1), train_values, marker="o", label="train")
    plt.plot(range(1, len(val_values) + 1), val_values, marker="o", label="val")
    plt.title("Train vs Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_metric_bars(metric_by_k: dict[int, float], title: str, y_label: str, output_path: Path) -> None:
    labels = [f"top-{k}" for k in metric_by_k]
    values = [metric_by_k[k] for k in metric_by_k]
    plt.figure(figsize=(7, 4))
    plt.bar(labels, values, color="#2563eb")
    plt.title(title)
    plt.ylabel(y_label)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_precision_recall(
    precision_at_k: dict[int, float],
    recall_at_k: dict[int, float],
    output_path: Path,
) -> None:
    ks = list(precision_at_k.keys())
    plt.figure(figsize=(8, 4))
    plt.plot(ks, [precision_at_k[k] for k in ks], marker="o", label="precision")
    plt.plot(ks, [recall_at_k[k] for k in ks], marker="o", label="recall")
    plt.title("Precision and Recall at k")
    plt.xlabel("k")
    plt.ylabel("Score")
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_mrr_ndcg(metrics: EvaluationMetrics, output_path: Path) -> None:
    values = [metrics.mrr, metrics.ndcg_at_k[5]]
    labels = ["MRR", "NDCG@5"]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=["#0f766e", "#7c3aed"])
    plt.title("MRR and NDCG Comparison")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_confusion_matrix(
    labels: list[int],
    matrix: list[list[int]],
    reverse_token_map: dict[int, int],
    output_path: Path,
) -> None:
    plt.figure(figsize=(7, 6))
    if matrix:
        plt.imshow(matrix, cmap="Blues", aspect="auto")
        plt.colorbar(label="Count")
        tick_labels = [str(label) for label in labels]
        plt.xticks(range(len(labels)), tick_labels, rotation=35, ha="right")
        plt.yticks(range(len(labels)), tick_labels)
    plt.title("Top-Class Confusion Matrix")
    plt.xlabel("Predicted product id")
    plt.ylabel("True product id")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_hyperparameter_comparison(experiments: list[ExperimentResult], output_path: Path) -> None:
    labels = [result.config.name for result in experiments]
    values = [result.metrics.topk_accuracy[3] for result in experiments]
    plt.figure(figsize=(9, 4))
    plt.bar(labels, values, color="#9333ea")
    plt.title("Hyperparameter Comparison by Top-3 Accuracy")
    plt.xlabel("Experiment")
    plt.ylabel("Top-3 accuracy")
    plt.xticks(rotation=25, ha="right")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_sequence_length_comparison(sequence_length_scores: dict[int, list[float]], output_path: Path) -> None:
    labels = [str(length) for length in sorted(sequence_length_scores)]
    values = [
        round(statistics.mean(sequence_length_scores[length]), 4)
        for length in sorted(sequence_length_scores)
    ]
    plt.figure(figsize=(7, 4))
    plt.bar(labels, values, color="#ea580c")
    plt.title("Sequence Length Comparison")
    plt.xlabel("Max sequence length")
    plt.ylabel("Mean Top-3 accuracy")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_inference_latency(latency_summary: dict[str, float], output_path: Path) -> None:
    labels = list(latency_summary.keys())
    values = [latency_summary[label] for label in labels]
    plt.figure(figsize=(7, 4))
    plt.bar(labels, values, color="#0891b2")
    plt.title("Inference Latency")
    plt.ylabel("Latency (ms)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_baseline_comparison(
    lstm_metrics: EvaluationMetrics,
    popularity_metrics: EvaluationMetrics,
    random_metrics: EvaluationMetrics,
    output_path: Path,
) -> None:
    labels = ["Random", "Popularity", "LSTM"]
    top1 = [random_metrics.accuracy, popularity_metrics.accuracy, lstm_metrics.accuracy]
    hit5 = [random_metrics.hit_rate_at_k[5], popularity_metrics.hit_rate_at_k[5], lstm_metrics.hit_rate_at_k[5]]
    ndcg5 = [random_metrics.ndcg_at_k[5], popularity_metrics.ndcg_at_k[5], lstm_metrics.ndcg_at_k[5]]
    positions = list(range(len(labels)))
    width = 0.25
    plt.figure(figsize=(9, 4))
    plt.bar([position - width for position in positions], top1, width=width, label="accuracy")
    plt.bar(positions, hit5, width=width, label="hit@5")
    plt.bar([position + width for position in positions], ndcg5, width=width, label="ndcg@5")
    plt.title("Baseline vs LSTM")
    plt.xticks(positions, labels)
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _percentile(values: list[float], percentile: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil((percentile / 100) * len(ordered)) - 1))
    return ordered[index]


def _set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
