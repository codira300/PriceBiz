import re

from typing import Optional

from app.database.connection import database
from app.database.validation import ProductVariantData
from app.utils import get_object_id


product_variants_collection = database.product_variants


async def create_product_variant(
    product_id: str,
    name: str,
    attributes: Optional[dict] = None,
):
    product_object_id = get_object_id(
        product_id,
        "product",
    )

    product_exists = await database.products.find_one(
        {"_id": product_object_id}
    )

    if product_exists is None:
        return None

    variant_data = ProductVariantData(
        name=name,
        attributes=attributes or {},
    )

    variant = {
        "product_id": product_object_id,
        **variant_data.model_dump(),
    }

    result = await product_variants_collection.insert_one(
        variant
    )

    return await product_variants_collection.find_one(
        {"_id": result.inserted_id}
    )


async def get_variant_by_id(
    variant_id: str,
):
    variant_object_id = get_object_id(
        variant_id,
        "product variant",
    )

    return await product_variants_collection.find_one(
        {"_id": variant_object_id}
    )


async def get_variants_by_product(
    product_id: str,
):
    product_object_id = get_object_id(
        product_id,
        "product",
    )

    cursor = product_variants_collection.find(
        {
            "product_id": product_object_id,
        }
    )

    return await cursor.to_list(length=None)


async def find_variant(
    product_id: str,
    name: Optional[str] = None,
):
    product_object_id = get_object_id(
        product_id,
        "product",
    )

    query = {
        "product_id": product_object_id,
    }

    if name:
        query["name"] = {
            "$regex": re.escape(name.strip()),
            "$options": "i",
        }

    return await product_variants_collection.find_one(
        query
    )


async def update_product_variant(
    variant_id: str,
    updates: dict,
):
    variant_object_id = get_object_id(
        variant_id,
        "product variant",
    )

    current = await product_variants_collection.find_one(
        {"_id": variant_object_id}
    )

    if current is None:
        return None

    product_id = current["product_id"]

    current_data = {
        key: value
        for key, value in current.items()
        if key not in {"_id", "product_id"}
    }

    merged = {
        **current_data,
        **updates,
    }

    validated = ProductVariantData(
        **merged
    )

    await product_variants_collection.update_one(
        {"_id": variant_object_id},
        {
            "$set": validated.model_dump(),
        },
    )

    return await get_variant_by_id(
        variant_id
    )