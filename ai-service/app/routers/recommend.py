from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas.recommend import RecommendationResponse
from app.services.recommend import recommend_products


router = APIRouter(tags=["recommend"])


@router.get("/recommend", response_model=RecommendationResponse)
def recommend(
    user_id: int = Query(..., ge=1),
    query: str | None = Query(None, min_length=1),
    limit: int = Query(5, ge=1, le=20),
    session: Session = Depends(get_session),
) -> RecommendationResponse:
    return recommend_products(session=session, user_id=user_id, query=query, limit=limit)
