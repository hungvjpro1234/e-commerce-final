from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db import get_session_factory, init_db
from app.main import app
from app.models.behavior import BehaviorEvent


client = TestClient(app)


def _reset_behavior_table() -> None:
    init_db()
    session = get_session_factory()()
    try:
        session.execute(delete(BehaviorEvent))
        session.commit()
    finally:
        session.close()


def test_post_behavior_persists_event():
    _reset_behavior_table()

    response = client.post(
        "/behavior",
        json={
            "user_id": 7,
            "product_id": 12,
            "action": "view",
            "timestamp": "2026-04-28T12:30:00Z",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["user_id"] == 7
    assert payload["product_id"] == 12
    assert payload["action"] == "view"


def test_get_user_behavior_returns_chronological_history():
    _reset_behavior_table()
    client.post(
        "/behavior",
        json={
            "user_id": 11,
            "query_text": "budget office chair",
            "action": "search",
            "timestamp": "2026-04-28T08:00:00Z",
        },
    )
    client.post(
        "/behavior",
        json={
            "user_id": 11,
            "product_id": 4,
            "action": "view",
            "timestamp": "2026-04-28T08:03:00Z",
        },
    )

    response = client.get("/behavior/user/11")

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == 11
    assert payload["total"] == 2
    assert payload["items"][0]["action"] == "search"
    assert payload["items"][1]["action"] == "view"


def test_search_event_requires_query_text():
    _reset_behavior_table()

    response = client.post(
        "/behavior",
        json={
            "user_id": 9,
            "action": "search",
            "timestamp": "2026-04-28T09:00:00Z",
        },
    )

    assert response.status_code == 422
