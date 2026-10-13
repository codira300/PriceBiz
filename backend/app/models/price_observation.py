from pydantic import BaseModel, Field
from typing import Any, Optional, Literal
from datetime import datetime


class Price(BaseModel):
    amount: int = Field(gt=0)
    currency: str = "NGN"


class Evidence(BaseModel):
    type: Literal[
        "USER_SUBMISSION",
        "PHOTO",
        "URL",
        "NOTE",
    ] = "USER_SUBMISSION"
    image_url: Optional[str] = None
    url: Optional[str] = None
    note: Optional[str] = None


class Feedback(BaseModel):
    useful: int = 0
    not_useful: int = 0
    reports: int = 0


class PriceObservation(BaseModel):
    product_id: str
    variant_id: str
    price: Price
    location_id: str
    source_id: str
    evidence: Optional[Evidence] = None
    feedback: Feedback = Field(default_factory=Feedback)
    observed_at: datetime
    status: str = "ACTIVE"


class RawSource(BaseModel):
    type: str
    name: str


class Processing(BaseModel):
    status: str
    observation_id: Optional[str] = None
    processed_at: Optional[datetime] = None


class RawObservation(BaseModel):
    source: RawSource
    input_format: str
    payload: dict[str, Any]
    processing: Processing
    created_at: datetime