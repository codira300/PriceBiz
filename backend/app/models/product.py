from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    status: str = "ACTIVE"