from typing import Optional

from app.database.connection import database
from app.database.validation import LocationData
from app.utils import get_object_id
from pymongo import ReturnDocument


locations_collection = database.locations


async def create_location(
    country: str,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    location_data = LocationData(
        country=country,
        state=state,
        lga=lga,
        area=area,
        market=market,
    )

    result = await locations_collection.insert_one(
        location_data.model_dump()
    )

    return await locations_collection.find_one(
        {"_id": result.inserted_id}
    )


async def get_location_by_id(location_id: str):
    location_object_id = get_object_id(
        location_id,
        "location",
    )

    return await locations_collection.find_one(
        {"_id": location_object_id}
    )


async def find_locations(
    country: Optional[str] = None,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    query = {}

    if country:
        query["country"] = country

    if state:
        query["state"] = state

    if lga:
        query["lga"] = lga

    if area:
        query["area"] = area

    if market:
        query["market"] = market

    cursor = locations_collection.find(query)

    return await cursor.to_list(length=None)


async def update_location(
    location_id: str,
    updates: dict,
):
    location_object_id = get_object_id(
        location_id,
        "location",
    )

    current = await locations_collection.find_one(
        {"_id": location_object_id}
    )

    if current is None:
        return None

    current.pop("_id", None)

    merged = {
        **current,
        **updates,
    }

    validated = LocationData(**merged)

    await locations_collection.update_one(
        {"_id": location_object_id},
        {
            "$set": validated.model_dump()
        },
    )

    return await get_location_by_id(location_id)


async def upsert_location(
    *,
    country: str,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    """
    Insert a location if it does not exist.
    Preserve the existing MongoDB _id if it already exists.
    """
    location_data = LocationData(
        country=country,
        state=state,
        lga=lga,
        area=area,
        market=market,
    ).model_dump()

    identity = {
        "country": location_data["country"],
        "state": location_data["state"],
        "lga": location_data["lga"],
        "area": location_data["area"],
        "market": location_data["market"],
    }

    return await locations_collection.find_one_and_update(
        identity,
        {"$setOnInsert": location_data},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
