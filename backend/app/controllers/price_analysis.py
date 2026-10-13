from typing import Optional

from app.database.product_variants import get_variant_by_id
from app.services import price_analysis as price_analysis_service


async def analyze_product_prices(
    *,
    product_id: str,
    location_id: Optional[str] = None,
):
    return await price_analysis_service.analyze_product_prices(
        product_id=product_id,
        location_id=location_id,
    )


async def analyze_variant_prices(
    *,
    product_id: str,
    variant_id: str,
    location_id: Optional[str] = None,
):
    return await price_analysis_service.analyze_variant_prices(
        product_id=product_id,
        variant_id=variant_id,
        location_id=location_id,
    )


async def analyze_variant_prices_by_id(
    *,
    variant_id: str,
    location_id: Optional[str] = None,
):
    variant = await get_variant_by_id(variant_id)

    if variant is None:
        return None

    product_id = str(variant["product_id"])

    return await analyze_variant_prices(
        product_id=product_id,
        variant_id=variant_id,
        location_id=location_id,
    )