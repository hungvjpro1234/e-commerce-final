from app.config import get_settings
from app.schemas.health import HealthResponse


def build_health_response() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        service=settings.app_name,
        status="ok",
        version="phase-9",
        dependencies={
            "ai_db": f"{settings.ai_db_engine}@{settings.ai_db_host}:{settings.ai_db_port}",
            "neo4j": settings.neo4j_uri,
            "product_service": settings.product_service_url,
        },
    )
