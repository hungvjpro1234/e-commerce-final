from pydantic import BaseModel


class HealthResponse(BaseModel):
    service: str
    status: str
    version: str
    dependencies: dict[str, str]
