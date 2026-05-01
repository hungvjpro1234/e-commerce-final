from pydantic import BaseModel


class GraphSyncResponse(BaseModel):
    product_count: int
    user_count: int
    interaction_edge_count: int
    similar_edge_count: int
    message: str


class GraphRecommendationItem(BaseModel):
    id: int
    name: str
    price: float
    category: str
    detail_type: str
    score: float
    reason: str


class GraphRecommendationResponse(BaseModel):
    user_id: int
    total: int
    items: list[GraphRecommendationItem]
