from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.clients.product_client import ProductServiceClient
from app.db import get_session
from app.graph.store import Neo4jGraphStore
from app.schemas.graph import GraphRecommendationResponse, GraphSyncResponse
from app.services.graph import get_graph_recommendations, sync_graph


router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/sync", response_model=GraphSyncResponse)
def graph_sync(session: Session = Depends(get_session)) -> GraphSyncResponse:
    with Neo4jGraphStore() as store:
        return sync_graph(session=session, store=store, client=ProductServiceClient())


@router.get("/recommend", response_model=GraphRecommendationResponse)
def graph_recommend(
    user_id: int = Query(..., ge=1),
    limit: int = Query(5, ge=1, le=20),
) -> GraphRecommendationResponse:
    with Neo4jGraphStore() as store:
        return get_graph_recommendations(user_id=user_id, store=store, limit=limit)
