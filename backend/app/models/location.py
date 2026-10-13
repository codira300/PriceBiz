from typing import Optional

from pydantic import BaseModel


class Coordinates(BaseModel):
    type: str = "Point"
    coordinates: list[float]


class Location(BaseModel):
    country: str
    state: Optional[str] = None
    lga: Optional[str] = None
    area: Optional[str] = None
    market: Optional[str] = None
    coordinates: Optional[Coordinates] = None