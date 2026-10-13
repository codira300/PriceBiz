from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from app.controllers import price_observations as price_observations_controller
from app.middleware.auth import get_current_user


router = APIRouter(
    prefix="/price-observations",
    tags=["Price Observations"],
)


class CreatePriceObservationRequest(BaseModel):
    product_id: str = Field(
        ...,
        min_length=1,
    )

    variant_id: str = Field(
        ...,
        min_length=1,
    )

    price: int = Field(
        ...,
        gt=0,
    )

    location_id: str = Field(
        ...,
        min_length=1,
    )

    observed_at: datetime

    source_id: Optional[str] = Field(
        default=None,
        min_length=1,
    )

    seller_type: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    evidence: dict[str, Any] = Field(
        default_factory=dict
    )


class UpdatePriceObservationRequest(BaseModel):
    price: Optional[int] = Field(
        default=None,
        gt=0,
    )

    observed_at: Optional[datetime] = None

    seller_type: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    evidence: Optional[dict[str, Any]] = None


class UpdatePriceObservationStatusRequest(BaseModel):
    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_price_observation(
    request: CreatePriceObservationRequest,
    current_user=Depends(get_current_user),
):
    return await (
        price_observations_controller
        .create_price_observation(
            product_id=request.product_id,
            variant_id=request.variant_id,
            price=request.price,
            location_id=request.location_id,
            observed_at=request.observed_at,
            source_id=request.source_id,
            submitted_by=str(current_user["_id"]),
            seller_type=request.seller_type,
            evidence=request.evidence,
        )
    )


@router.get("")
async def find_price_observations(
    product_id: Optional[str] = Query(
        default=None
    ),
    variant_id: Optional[str] = Query(
        default=None
    ),
    location_id: Optional[str] = Query(
        default=None
    ),
    source_id: Optional[str] = Query(
        default=None
    ),
    submitted_by: Optional[str] = Query(
        default=None
    ),
    seller_type: Optional[str] = Query(
        default=None
    ),
    observation_status: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
):
    return await (
        price_observations_controller
        .find_price_observations(
            product_id=product_id,
            variant_id=variant_id,
            location_id=location_id,
            source_id=source_id,
            submitted_by=submitted_by,
            seller_type=seller_type,
            status=observation_status,
            limit=limit,
            skip=skip,
        )
    )


@router.get("/product/{product_id}")
async def get_product_price_observations(
    product_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):
    return await (
        price_observations_controller
        .get_product_price_observations(
            product_id=product_id,
            limit=limit,
        )
    )


@router.get("/location/{location_id}")
async def get_location_price_observations(
    location_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):
    return await (
        price_observations_controller
        .get_location_price_observations(
            location_id=location_id,
            limit=limit,
        )
    )


@router.get("/user/{user_id}")
async def get_user_price_observations(
    user_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):
    return await (
        price_observations_controller
        .get_user_price_observations(
            user_id=user_id,
            limit=limit,
        )
    )


@router.get("/{observation_id}")
async def get_price_observation(
    observation_id: str,
):
    return await (
        price_observations_controller
        .get_price_observation(
            observation_id=observation_id,
        )
    )


@router.patch("/{observation_id}")
async def update_price_observation(
    observation_id: str,
    request: UpdatePriceObservationRequest,
    current_user=Depends(get_current_user),
):
    updates = request.model_dump(
        exclude_unset=True
    )

    return await (
        price_observations_controller
        .update_price_observation(
            observation_id=observation_id,
            updates=updates,
        )
    )


@router.patch("/{observation_id}/status")
async def update_price_observation_status(
    observation_id: str,
    request: UpdatePriceObservationStatusRequest,
    current_user=Depends(get_current_user),
):
    return await (
        price_observations_controller
        .update_price_observation_status(
            observation_id=observation_id,
            status=request.status,
        )
    )