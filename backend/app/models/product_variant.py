from pydantic import BaseModel
from typing import Optional


class ProductVariant(BaseModel):
    product_id: str
    name: str
    attributes: Optional[dict] = None
    status: str = "ACTIVE"