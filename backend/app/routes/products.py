from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.controllers import products as products_controller
from app.middleware.auth import get_current_user


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


class CreateProductRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )
    brand: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    category: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
    )
    packaging: dict[str, Any] = Field(
        default_factory=dict,
    )
    variant_name: Optional[str] = Field(
        default=None,
        max_length=200,
    )
    variant_attributes: dict[str, Any] = Field(
        default_factory=dict,
    )


class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    brand: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    category: Optional[str] = Field(
        default=None,
        max_length=100,
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
    )
    details: Optional[dict[str, Any]] = None
    packaging: Optional[dict[str, Any]] = None


@router.get("/")
async def get_products(
    q: Optional[str] = Query(
        default=None,
        min_length=1,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
):
    if q is not None:
        return await products_controller.search_products(
            query=q,
            limit=limit,
            skip=skip,
        )

    return await products_controller.list_products(
        limit=limit,
        skip=skip,
    )


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    include_variants: bool = Query(
        default=True,
    ),
):
    return await products_controller.get_product(
        product_id=product_id,
        include_variants=include_variants,
    )


@router.post("/")
async def create_product(
    request: CreateProductRequest,
    current_user=Depends(get_current_user),
):
    return await products_controller.create_product(
        creator_id=str(current_user["_id"]),
        name=request.name,
        brand=request.brand,
        category=request.category,
        description=request.description,
        details=request.details,
        packaging=request.packaging,
        variant_name=request.variant_name,
        variant_attributes=request.variant_attributes,
    )


@router.patch("/{product_id}")
async def update_product(
    product_id: str,
    request: UpdateProductRequest,
    current_user=Depends(get_current_user),
):
    updates = request.model_dump(
        exclude_unset=True,
    )

    return await products_controller.update_product(
        product_id=product_id,
        user_id=str(current_user["_id"]),
        updates=updates,
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user=Depends(get_current_user),
):
    return await products_controller.delete_product(
        product_id=product_id,
        user_id=str(current_user["_id"]),
    )