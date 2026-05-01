from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas.behavior import BehaviorEventCreate, BehaviorEventResponse, UserBehaviorHistoryResponse
from app.services.behavior import create_behavior_event, list_behavior_for_user


router = APIRouter(prefix="/behavior", tags=["behavior"])


@router.post("", response_model=BehaviorEventResponse, status_code=status.HTTP_201_CREATED)
def ingest_behavior_event(
    payload: BehaviorEventCreate,
    session: Session = Depends(get_session),
) -> BehaviorEventResponse:
    return create_behavior_event(session=session, payload=payload)


@router.get("/user/{user_id}", response_model=UserBehaviorHistoryResponse)
def get_user_behavior_history(
    user_id: int,
    session: Session = Depends(get_session),
) -> UserBehaviorHistoryResponse:
    return list_behavior_for_user(session=session, user_id=user_id)
