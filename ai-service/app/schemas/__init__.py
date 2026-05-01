"""Pydantic schemas for AI service."""
from app.schemas.behavior import BehaviorEventCreate, BehaviorEventResponse, UserBehaviorHistoryResponse
from app.schemas.graph import GraphRecommendationItem, GraphRecommendationResponse, GraphSyncResponse
from app.schemas.health import HealthResponse
from app.schemas.product import CategoryData, ProductCatalogItem
from app.schemas.rag import RagRebuildResponse, RagRetrievedProduct

__all__ = [
    "BehaviorEventCreate",
    "BehaviorEventResponse",
    "CategoryData",
    "GraphRecommendationItem",
    "GraphRecommendationResponse",
    "GraphSyncResponse",
    "HealthResponse",
    "ProductCatalogItem",
    "RagRebuildResponse",
    "RagRetrievedProduct",
    "UserBehaviorHistoryResponse",
]
