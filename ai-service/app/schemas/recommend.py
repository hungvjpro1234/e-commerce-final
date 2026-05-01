from __future__ import annotations

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    id: int
    name: str
    price: float
    category: str
    detail_type: str
    score: float
    reason: str
    source_scores: dict[str, float]


class RecommendationResponse(BaseModel):
    user_id: int
    query: str | None = None
    total: int
    items: list[RecommendationItem]
    sources_used: list[str]

