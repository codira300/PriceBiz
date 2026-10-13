from typing import Any, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.controllers import product_variants as product_variants_controller


router = APIRouter(
    prefix="/product-variants",
    tags=["Product Variants"],
)


class CreateProductVariantRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    attributes: dict[str, Any] = Field(default_factory=dict)


class UpdateProductVariantRequest(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    attributes: Optional[dict[str, Any]] = None


@router.post("/")
async def create_product_variant(
    request: CreateProductVariantRequest,
):
    return await product_variants_controller.create_product_variant(
        product_id=request.product_id,
        name=request.name,
        attributes=request.attributes,
    )


@router.get("/product/{product_id}")
async def get_product_variants(
    product_id: str,
):
    return await product_variants_controller.get_product_variants(
        product_id=product_id,
    )


@router.get("/product/{product_id}/find")
async def find_product_variant(
    product_id: str,
    name: Optional[str] = Query(default=None),
):
    return await product_variants_controller.find_product_variant(
        product_id=product_id,
        name=name,
    )


@router.get("/{variant_id}")
async def get_product_variant(
    variant_id: str,
):
    return await product_variants_controller.get_product_variant(
        variant_id=variant_id,
    )


@router.patch("/{variant_id}")
async def update_product_variant(
    variant_id: str,
    request: UpdateProductVariantRequest,
):
    return await product_variants_controller.update_product_variant(
        variant_id=variant_id,
        name=request.name,
        attributes=request.attributes,
    )