from typing import Any, Optional

from app.services import product_variants as product_variants_service


def serialize_product_variant(variant: dict):
    return {
        "_id": str(variant["_id"]),
        "product_id": str(variant["product_id"]),
        "name": variant.get("name"),
        "attributes": variant.get("attributes", {}),
    }


async def create_product_variant(
    *,
    product_id: str,
    name: str,
    attributes: Optional[dict[str, Any]] = None,
):
    variant = await product_variants_service.create_product_variant(
        product_id=product_id,
        name=name,
        attributes=attributes,
    )

    return serialize_product_variant(variant)


async def get_product_variant(
    *,
    variant_id: str,
):
    variant = await product_variants_service.get_product_variant(
        variant_id=variant_id,
    )

    return serialize_product_variant(variant)


async def get_product_variants(
    *,
    product_id: str,
):
    variants = await product_variants_service.get_product_variants(
        product_id=product_id,
    )

    return [
        serialize_product_variant(variant)
        for variant in variants
    ]


async def find_product_variant(
    *,
    product_id: str,
    name: Optional[str] = None,
):
    variant = await product_variants_service.find_product_variant(
        product_id=product_id,
        name=name,
    )

    if variant is None:
        return None

    return serialize_product_variant(variant)


async def update_product_variant(
    *,
    variant_id: str,
    name: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
):
    variant = await product_variants_service.update_product_variant(
        variant_id=variant_id,
        name=name,
        attributes=attributes,
    )

    return serialize_product_variant(variant)