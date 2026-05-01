from __future__ import annotations

from pydantic import BaseModel, Field


class ChatbotRequest(BaseModel):
    user_id: int | None = Field(default=None, ge=1)
    message: str = Field(min_length=2)


class ChatbotProductSuggestion(BaseModel):
    id: int
    name: str
    price: float
    category: str
    detail_type: str
    score: float
    reason: str


class ChatbotResponse(BaseModel):
    answer: str
    products: list[ChatbotProductSuggestion]
    retrieved_context: list[str]
    query_type: str
