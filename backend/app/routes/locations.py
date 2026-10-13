from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.controllers import locations as locations_controller


router = APIRouter(
    prefix="/locations",
    tags=["Locations"],
)


class CreateLocationRequest(BaseModel):
    country: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    state: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    lga: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    area: Optional[str] = Field(
        default=None,
        max_length=150,
    )
    market: Optional[str] = Field(
        default=None,
        max_length=150,
    )


class UpdateLocationRequest(BaseModel):
    country: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    state: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    lga: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    area: Optional[str] = Field(
        default=None,
        max_length=150,
    )
    market: Optional[str] = Field(
        default=None,
        max_length=150,
    )


@router.get("/")
async def get_locations(
    country: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    lga: Optional[str] = Query(default=None),
    area: Optional[str] = Query(default=None),
    market: Optional[str] = Query(default=None),
):
    return await locations_controller.find_locations(
        country=country,
        state=state,
        lga=lga,
        area=area,
        market=market,
    )


@router.get("/{location_id}")
async def get_location(
    location_id: str,
):
    return await locations_controller.get_location(
        location_id=location_id,
    )


@router.post("/")
async def create_location(
    request: CreateLocationRequest,
):
    return await locations_controller.create_location(
        country=request.country,
        state=request.state,
        lga=request.lga,
        area=request.area,
        market=request.market,
    )


@router.patch("/{location_id}")
async def update_location(
    location_id: str,
    request: UpdateLocationRequest,
):
    return await locations_controller.update_location(
        location_id=location_id,
        country=request.country,
        state=request.state,
        lga=request.lga,
        area=request.area,
        market=request.market,
    )