from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.config import get_settings
from app.db import init_db
from app.routers.behavior import router as behavior_router
from app.routers.chatbot import router as chatbot_router
from app.routers.graph import router as graph_router
from app.routers.health import router as health_router
from app.routers.rag import router as rag_router
from app.routers.recommend import router as recommend_router


settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Service",
    version="0.2.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(behavior_router)
app.include_router(graph_router)
app.include_router(rag_router)
app.include_router(recommend_router)
app.include_router(chatbot_router)
