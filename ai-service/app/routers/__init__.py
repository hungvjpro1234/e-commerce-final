"""API routers for AI service."""
from app.routers.behavior import router as behavior_router
from app.routers.graph import router as graph_router
from app.routers.health import router as health_router
from app.routers.rag import router as rag_router

__all__ = ["behavior_router", "graph_router", "health_router", "rag_router"]
