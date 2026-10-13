from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.controllers import price_analysis as price_analysis_controller
from app.utils import get_object_id


router = APIRouter(
    prefix="/price-analysis",
    tags=["Price Analysis"],
)


@router.get("/product/{product_id}")
async def get_product_price_analysis(
    product_id: str,
    location_id: Optional[str] = Query(default=None),
):
    get_object_id(product_id, "product")

    if location_id is not None:
        get_object_id(location_id, "location")

    result = await price_analysis_controller.analyze_product_prices(
        product_id=product_id,
        location_id=location_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return result


@router.get("/variant/{variant_id}")
async def get_variant_price_analysis(
    variant_id: str,
    location_id: Optional[str] = Query(default=None),
):
    get_object_id(variant_id, "product variant")

    if location_id is not None:
        get_object_id(location_id, "location")

    result = await price_analysis_controller.analyze_variant_prices_by_id(
        variant_id=variant_id,
        location_id=location_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Product variant not found",
        )

    return result