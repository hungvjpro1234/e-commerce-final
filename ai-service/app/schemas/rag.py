from pydantic import BaseModel


class RagRebuildResponse(BaseModel):
    message: str
    method: str
    document_count: int
    artifact_paths: dict[str, str]


class RagRetrievedProduct(BaseModel):
    id: int
    name: str
    price: float
    category: str
    detail_type: str
    score: float
    matched_terms: list[str]
    document_text: str
