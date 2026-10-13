from datetime import datetime, timezone
from typing import Optional

from app.database.connection import database
from app.database.validation import PriceObservationData
from app.utils import get_object_id


price_observations_collection = database.price_observations


async def create_price_observation(
    product_id: str,
    variant_id: str,
    price: int,
    location_id: str,
    observed_at: datetime,
    source_id: Optional[str] = None,
    submitted_by: Optional[str] = None,
    seller_type: Optional[str] = None,
    evidence: Optional[dict] = None,
):
    product_object_id = get_object_id(product_id, "product")
    variant_object_id = get_object_id(
        variant_id,
        "product variant",
    )
    location_object_id = get_object_id(
        location_id,
        "location",
    )

    product = await database.products.find_one(
        {"_id": product_object_id}
    )

    if product is None:
        return None

    variant = await database.product_variants.find_one(
        {
            "_id": variant_object_id,
            "product_id": product_object_id,
        }
    )

    if variant is None:
        return None

    location = await database.locations.find_one(
        {"_id": location_object_id}
    )

    if location is None:
        return None

    if source_id:
        source_object_id = get_object_id(
            source_id,
            "source",
        )

        source = await database.sources.find_one(
            {"_id": source_object_id}
        )

        if source is None:
            return None
    else:
        source_object_id = None

    if submitted_by:
        user_object_id = get_object_id(
            submitted_by,
            "user",
        )

        user = await database.users.find_one(
            {"_id": user_object_id}
        )

        if user is None:
            return None
    else:
        user_object_id = None

    observation_data = PriceObservationData(
        price={
            "amount": price,
            "currency": "NGN",
        },
        observed_at=observed_at,
        seller_type=seller_type,
        evidence=evidence or {},
    )

    now = datetime.now(timezone.utc)

    observation = {
        "product_id": product_object_id,
        "variant_id": variant_object_id,
        "location_id": location_object_id,
        "source_id": source_object_id,
        "submitted_by": user_object_id,
        **observation_data.model_dump(),
        "status": "ACTIVE",
        "feedback": {
            "useful": 0,
            "not_useful": 0,
            "reports": 0,
        },
        "created_at": now,
        "updated_at": now,
    }

    result = await price_observations_collection.insert_one(
        observation
    )

    return await price_observations_collection.find_one(
        {"_id": result.inserted_id}
    )


async def get_price_observation_by_id(
    observation_id: str,
):
    observation_object_id = get_object_id(
        observation_id,
        "price observation",
    )

    return await price_observations_collection.find_one(
        {"_id": observation_object_id}
    )


async def find_price_observations(
    *,
    product_id: Optional[str] = None,
    variant_id: Optional[str] = None,
    location_id: Optional[str] = None,
    source_id: Optional[str] = None,
    submitted_by: Optional[str] = None,
    seller_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
):
    query = {}

    if product_id:
        query["product_id"] = get_object_id(
            product_id,
            "product",
        )

    if variant_id:
        query["variant_id"] = get_object_id(
            variant_id,
            "product variant",
        )

    if location_id:
        query["location_id"] = get_object_id(
            location_id,
            "location",
        )

    if source_id:
        query["source_id"] = get_object_id(
            source_id,
            "source",
        )

    if submitted_by:
        query["submitted_by"] = get_object_id(
            submitted_by,
            "user",
        )

    if seller_type:
        query["seller_type"] = seller_type.upper()

    if status:
        query["status"] = status.upper()

    cursor = (
        price_observations_collection
        .find(query)
        .sort("observed_at", -1)
        .skip(skip)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def get_price_observations_by_product(
    product_id: str,
    limit: int = 50,
):
    product_object_id = get_object_id(
        product_id,
        "product",
    )

    cursor = (
        price_observations_collection
        .find({
            "product_id": product_object_id,
        })
        .sort("observed_at", -1)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def get_price_observations_by_location(
    location_id: str,
    limit: int = 50,
):
    location_object_id = get_object_id(
        location_id,
        "location",
    )

    cursor = (
        price_observations_collection
        .find({
            "location_id": location_object_id,
        })
        .sort("observed_at", -1)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def get_price_observations_by_user(
    user_id: str,
    limit: int = 50,
):
    user_object_id = get_object_id(
        user_id,
        "user",
    )

    cursor = (
        price_observations_collection
        .find({
            "submitted_by": user_object_id,
        })
        .sort("observed_at", -1)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def update_price_observation(
    observation_id: str,
    updates: dict,
):
    observation_object_id = get_object_id(
        observation_id,
        "price observation",
    )

    current = await price_observations_collection.find_one(
        {"_id": observation_object_id}
    )

    if current is None:
        return None

    allowed_fields = {
        "price",
        "observed_at",
        "seller_type",
        "evidence",
    }

    filtered_updates = {
        key: value
        for key, value in updates.items()
        if key in allowed_fields
    }

    if not filtered_updates:
        return current

    merged = {
        "price": current["price"],
        "observed_at": current["observed_at"],
        "seller_type": current.get("seller_type"),
        "evidence": current.get("evidence", {}),
        **filtered_updates,
    }

    validated = PriceObservationData(**merged)

    await price_observations_collection.update_one(
        {"_id": observation_object_id},
        {
            "$set": {
                **validated.model_dump(),
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return await get_price_observation_by_id(
        observation_id
    )


async def update_price_observation_status(
    observation_id: str,
    status: str,
):
    observation_object_id = get_object_id(
        observation_id,
        "price observation",
    )

    result = await price_observations_collection.update_one(
        {"_id": observation_object_id},
        {
            "$set": {
                "status": status.upper(),
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    if result.matched_count == 0:
        return None

    return await get_price_observation_by_id(
        observation_id
    )


async def increment_feedback(
    observation_id: str,
    feedback_type: str,
):
    observation_object_id = get_object_id(
        observation_id,
        "price observation",
    )

    field_map = {
        "useful": "feedback.useful",
        "not_useful": "feedback.not_useful",
        "reports": "feedback.reports",
    }

    field = field_map.get(feedback_type)

    if field is None:
        raise ValueError("Invalid feedback type")

    result = await price_observations_collection.update_one(
        {"_id": observation_object_id},
        {
            "$inc": {
                field: 1,
            },
            "$set": {
                "updated_at": datetime.now(timezone.utc),
            },
        },
    )

    if result.matched_count == 0:
        return None

    return await get_price_observation_by_id(
        observation_id
    )