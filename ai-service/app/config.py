import os
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = Field(default_factory=lambda: os.getenv("APP_NAME", "ai-service"))
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True") == "True")
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8007")))

    ai_db_engine: Literal["postgresql", "mysql", "sqlite"] = Field(
        default_factory=lambda: os.getenv("AI_DB_ENGINE", "postgresql")
    )
    ai_db_name: str = Field(default_factory=lambda: os.getenv("AI_DB_NAME", "ai_db"))
    ai_db_user: str = Field(default_factory=lambda: os.getenv("AI_DB_USER", "ai_user"))
    ai_db_password: str = Field(default_factory=lambda: os.getenv("AI_DB_PASSWORD", "ai_pass"))
    ai_db_host: str = Field(default_factory=lambda: os.getenv("AI_DB_HOST", "ai-db"))
    ai_db_port: int = Field(default_factory=lambda: int(os.getenv("AI_DB_PORT", "5432")))

    neo4j_uri: str = Field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://neo4j:7687"))
    neo4j_user: str = Field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    neo4j_password: str = Field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "neo4jpassword"))

    product_service_url: str = Field(default_factory=lambda: os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8001"))
    product_service_timeout_seconds: int = Field(default_factory=lambda: int(os.getenv("PRODUCT_SERVICE_TIMEOUT_SECONDS", "10")))
    product_service_max_retries: int = Field(default_factory=lambda: int(os.getenv("PRODUCT_SERVICE_MAX_RETRIES", "2")))
    order_service_url: str = Field(default_factory=lambda: os.getenv("ORDER_SERVICE_URL", "http://order-service:8004"))
    artifacts_dir: str = Field(default_factory=lambda: os.getenv("ARTIFACTS_DIR", "/app/artifacts"))
    docs_artifacts_dir: str = Field(default_factory=lambda: os.getenv("DOCS_ARTIFACTS_DIR", "/workspace-docs/ai-service/artifacts"))
    synthetic_behavior_seed: int = Field(default_factory=lambda: int(os.getenv("SYNTHETIC_BEHAVIOR_SEED", "20260428")))
    lstm_training_seed: int = Field(default_factory=lambda: int(os.getenv("LSTM_TRAINING_SEED", "20260430")))
    lstm_default_epochs: int = Field(default_factory=lambda: int(os.getenv("LSTM_DEFAULT_EPOCHS", "18")))


@lru_cache
def get_settings() -> Settings:
    return Settings()
