from datetime import datetime, timezone
from typing import Any, Optional

from app.database.connection import database
from app.database.validation import ProductData
from app.utils import get_object_id


products_collection = database.products


async def create_product(
    creator_id: str,
    name: str,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    packaging: Optional[dict[str, Any]] = None,
):
    creator_object_id = get_object_id(
        creator_id,
        "user",
    )

    creator = await database.users.find_one(
        {"_id": creator_object_id}
    )

    if creator is None:
        return None

    product_data = ProductData(
        name=name,
        brand=brand,
        category=category,
        description=description,
    )

    now = datetime.now(timezone.utc)

    product = {
        **product_data.model_dump(),
        "creator_id": creator_object_id,
        "details": details or {},
        "packaging": packaging or {},
        "created_at": now,
        "updated_at": now,
    }

    result = await products_collection.insert_one(product)

    return await products_collection.find_one(
        {"_id": result.inserted_id}
    )


async def get_product_by_id(product_id: str):
    object_id = get_object_id(
        product_id,
        "product",
    )

    return await products_collection.find_one(
        {"_id": object_id}
    )


async def find_products(
    name: Optional[str] = None,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
):
    query = {}

    if name:
        query["name"] = {
            "$regex": name,
            "$options": "i",
        }

    if brand:
        query["brand"] = {
            "$regex": brand,
            "$options": "i",
        }

    if category:
        query["category"] = {
            "$regex": category,
            "$options": "i",
        }

    cursor = (
        products_collection
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def update_product(
    product_id: str,
    updates: dict,
):
    object_id = get_object_id(
        product_id,
        "product",
    )

    current = await products_collection.find_one(
        {"_id": object_id}
    )

    if current is None:
        return None

    current.pop("_id", None)
    current.pop("creator_id", None)
    current.pop("created_at", None)

    merged = {
        **current,
        **updates,
    }

    validated = ProductData(
        name=merged["name"],
        brand=merged.get("brand"),
        category=merged.get("category"),
        description=merged.get("description"),
    )

    update_data = {
        **validated.model_dump(),
        "details": merged.get("details", {}),
        "packaging": merged.get("packaging", {}),
        "updated_at": datetime.now(timezone.utc),
    }

    await products_collection.update_one(
        {"_id": object_id},
        {"$set": update_data},
    )

    return await get_product_by_id(product_id)


async def delete_product(product_id: str):
    object_id = get_object_id(
        product_id,
        "product",
    )

    result = await products_collection.delete_one(
        {"_id": object_id}
    )

    return result.deleted_count > 0