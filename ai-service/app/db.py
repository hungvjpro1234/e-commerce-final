from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def get_database_dsn() -> str:
    settings = get_settings()
    if settings.ai_db_engine == "postgresql":
        return (
            f"postgresql+psycopg://{settings.ai_db_user}:{settings.ai_db_password}"
            f"@{settings.ai_db_host}:{settings.ai_db_port}/{settings.ai_db_name}"
        )

    if settings.ai_db_engine == "mysql":
        return (
            f"mysql+pymysql://{settings.ai_db_user}:{settings.ai_db_password}"
            f"@{settings.ai_db_host}:{settings.ai_db_port}/{settings.ai_db_name}"
        )

    if settings.ai_db_name == ":memory:":
        return "sqlite+pysqlite:///:memory:"

    return f"sqlite+pysqlite:///{settings.ai_db_name}"


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    connect_args: dict[str, object] = {}
    if settings.ai_db_engine == "sqlite":
        connect_args["check_same_thread"] = False

    return create_engine(
        get_database_dsn(),
        pool_pre_ping=True,
        future=True,
        connect_args=connect_args,
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    from app.models.behavior import BehaviorEvent

    Base.metadata.create_all(bind=get_engine(), tables=[BehaviorEvent.__table__])
