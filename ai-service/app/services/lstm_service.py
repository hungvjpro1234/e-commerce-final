from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import torch
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.ml.lstm_model import NextProductLSTM
from app.models.behavior import BehaviorEvent


@dataclass(frozen=True)
class LstmRecommendation:
    product_id: int
    score: float


@dataclass(frozen=True)
class LstmInferenceResult:
    items: list[LstmRecommendation]
    source: str
    reason: str


class LstmRecommendationService:
    def __init__(self) -> None:
        settings = get_settings()
        self.runtime_dir = Path(settings.artifacts_dir) / "lstm"
        self.model_path = self.runtime_dir / "best_lstm_model.pt"
        self.metadata_path = self.runtime_dir / "lstm_metadata.json"
        self._runtime_payload: dict[str, object] | None = None
        self._model: NextProductLSTM | None = None

    def recommend_for_user(self, session: Session, user_id: int, top_k: int = 5) -> LstmInferenceResult:
        history = self._load_user_history(session=session, user_id=user_id)
        return self.recommend_from_history(history=history, top_k=top_k)

    def recommend_from_history(self, history: list[int], top_k: int = 5) -> LstmInferenceResult:
        runtime_payload = self._load_runtime_payload()
        if runtime_payload is None:
            return self._fallback_result(reason="model artifact not available", top_k=top_k)

        min_history = int(runtime_payload.get("min_history", 2))
        if len(history) < min_history:
            return self._fallback_result(reason="user history too short", top_k=top_k)

        model = self._load_model()
        if model is None:
            return self._fallback_result(reason="model artifact not available", top_k=top_k)

        product_id_to_token = {int(key): int(value) for key, value in dict(runtime_payload["product_id_to_token"]).items()}
        token_to_product_id = {int(key): int(value) for key, value in dict(runtime_payload["token_to_product_id"]).items()}
        config = dict(runtime_payload["config"])
        sequence_length = int(config["max_sequence_length"])
        encoded_history = [product_id_to_token[product_id] for product_id in history if product_id in product_id_to_token]
        if len(encoded_history) < min_history:
            return self._fallback_result(reason="history does not map to trained vocabulary", top_k=top_k)

        encoded_history = encoded_history[-sequence_length:]
        inputs = torch.tensor([encoded_history], dtype=torch.long)
        lengths = torch.tensor([len(encoded_history)], dtype=torch.long)
        with torch.no_grad():
            logits = model(inputs, lengths)
            probabilities = torch.softmax(logits, dim=1)
            prediction_tokens = torch.topk(probabilities, k=min(top_k, probabilities.shape[1] - 1), dim=1).indices[0].tolist()
            prediction_scores = torch.topk(probabilities, k=min(top_k, probabilities.shape[1] - 1), dim=1).values[0].tolist()

        items: list[LstmRecommendation] = []
        for token, score in zip(prediction_tokens, prediction_scores, strict=False):
            product_id = token_to_product_id.get(int(token))
            if product_id is None:
                continue
            items.append(LstmRecommendation(product_id=product_id, score=round(float(score), 4)))

        if not items:
            return self._fallback_result(reason="no prediction candidates available", top_k=top_k)
        return LstmInferenceResult(items=items, source="lstm", reason="predicted from user interaction sequence")

    def _load_user_history(self, session: Session, user_id: int) -> list[int]:
        rows = session.scalars(
            select(BehaviorEvent)
            .where(BehaviorEvent.user_id == user_id, BehaviorEvent.product_id.is_not(None))
            .order_by(BehaviorEvent.timestamp.asc(), BehaviorEvent.id.asc())
        ).all()
        return [int(row.product_id) for row in rows if row.action != "search" and row.product_id is not None]

    def _load_model(self) -> NextProductLSTM | None:
        runtime_payload = self._load_runtime_payload()
        if runtime_payload is None:
            return None
        if self._model is not None:
            return self._model

        config = dict(runtime_payload["config"])
        vocab_size = len(dict(runtime_payload["product_id_to_token"]))
        checkpoint = torch.load(self.model_path, map_location="cpu")
        model = NextProductLSTM(
            vocab_size=vocab_size,
            embedding_dim=int(config["embedding_dim"]),
            hidden_dim=int(config["hidden_dim"]),
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        self._model = model
        return model

    def _load_runtime_payload(self) -> dict[str, object] | None:
        if self._runtime_payload is not None:
            return self._runtime_payload
        if not self.metadata_path.exists():
            return None
        self._runtime_payload = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        return self._runtime_payload

    def _fallback_result(self, reason: str, top_k: int) -> LstmInferenceResult:
        runtime_payload = self._load_runtime_payload()
        popularity_ranking = []
        if runtime_payload is not None:
            popularity_ranking = [int(product_id) for product_id in runtime_payload.get("popularity_ranking", [])]
        items = [
            LstmRecommendation(product_id=product_id, score=round(1 / (index + 1), 4))
            for index, product_id in enumerate(popularity_ranking[:top_k])
        ]
        return LstmInferenceResult(items=items, source="popularity", reason=reason)
