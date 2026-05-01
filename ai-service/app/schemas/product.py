from typing import Any

from pydantic import BaseModel, ConfigDict


class CategoryData(BaseModel):
    id: int
    name: str


class ProductCatalogItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    price: float
    stock: int
    category: int
    category_data: CategoryData
    detail_type: str
    detail: dict[str, Any]
