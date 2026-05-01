from fastapi import APIRouter

from app.schemas.rag import RagRebuildResponse
from app.services.rag import rebuild_rag_index


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/rebuild-index", response_model=RagRebuildResponse)
def rebuild_index() -> RagRebuildResponse:
    return rebuild_rag_index()
