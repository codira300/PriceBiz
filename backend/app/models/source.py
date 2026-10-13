from pydantic import BaseModel
from typing import Literal


class Source(BaseModel):
    type: Literal[
        "COMMUNITY",
        "RETAILER",
        "GOVERNMENT",
        "RESEARCH",
        "ADMIN",
        "IMPORTED_DATA"
    ]
    name: str
    verification_status: str = "UNVERIFIED"