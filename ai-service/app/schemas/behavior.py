from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


BehaviorActionLiteral = Literal["view", "click", "search", "add_to_cart", "buy"]


class BehaviorEventCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    product_id: int | None = Field(default=None, ge=1)
    action: BehaviorActionLiteral
    query_text: str | None = None
    timestamp: datetime | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "BehaviorEventCreate":
        if self.action == "search":
            if not self.query_text:
                raise ValueError("query_text is required for search events")
        elif self.product_id is None:
            raise ValueError("product_id is required for non-search events")

        if self.timestamp is None:
            self.timestamp = datetime.now(UTC)

        return self


class BehaviorEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int | None
    action: BehaviorActionLiteral
    query_text: str | None
    timestamp: datetime


class UserBehaviorHistoryResponse(BaseModel):
    user_id: int
    total: int
    items: list[BehaviorEventResponse]
