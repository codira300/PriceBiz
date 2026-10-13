from typing import Optional
from datetime import datetime, timezone
from app.database.connection import database
from app.database.validation import RawObservationData
from app.utils import get_object_id


raw_observations_collection = database.raw_observations


async def create_raw_observation(
    input_format: str,
    payload: dict,
    source_id: Optional[str] = None,
    processing_status: str = "PENDING",
):
    raw_data = RawObservationData(
        input_format=input_format,
        payload=payload,
        processing_status=processing_status,
    )

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

    observation = {
        **raw_data.model_dump(),
        "source_id": source_object_id,
    }

    result = await raw_observations_collection.insert_one(
        observation
    )

    return await raw_observations_collection.find_one(
        {"_id": result.inserted_id}
    )


async def get_raw_observation_by_id(
    observation_id: str,
):
    observation_object_id = get_object_id(
        observation_id,
        "raw observation",
    )

    return await raw_observations_collection.find_one(
        {"_id": observation_object_id}
    )


async def get_raw_observations_by_status(
    processing_status: str,
):
    cursor = raw_observations_collection.find(
        {
            "processing_status": processing_status.upper()
        }
    )

    return await cursor.to_list(length=None)


async def get_raw_observations_by_format(
    input_format: str,
):
    cursor = raw_observations_collection.find(
        {
            "input_format": input_format.upper()
        }
    )

    return await cursor.to_list(length=None)


async def update_processing_status(
    observation_id: str,
    processing_status: str,
):
    observation_object_id = get_object_id(
        observation_id,
        "raw observation",
    )

    current = await raw_observations_collection.find_one(
        {"_id": observation_object_id}
    )

    if current is None:
        return None

    current_status = RawObservationData(
        input_format=current["input_format"],
        payload=current["payload"],
        processing_status=processing_status,
    )

    await raw_observations_collection.update_one(
        {"_id": observation_object_id},
        {
            "$set": {
                "processing_status":
                    current_status.processing_status
            }
        },
    )

    return await get_raw_observation_by_id(
        observation_id
    )
    
    
async def update_processing_result(
    observation_id: str,
    price_observation_id: str,
):
    observation_object_id = get_object_id(
        observation_id,
        "raw observation",
    )

    price_observation_object_id = get_object_id(
        price_observation_id,
        "price observation",
    )

    result = await raw_observations_collection.update_one(
        {"_id": observation_object_id},
        {
            "$set": {
                "processing_status": "PROCESSED",
                "processing_result": {
                    "price_observation_id": price_observation_object_id,
                },
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    if result.matched_count == 0:
        return None

    return await get_raw_observation_by_id(observation_id)


async def find_raw_observations(
    *,
    input_format: Optional[str] = None,
    processing_status: Optional[str] = None,
    source_id: Optional[str] = None,
):
    query = {}

    if input_format:
        query["input_format"] = input_format.upper()

    if processing_status:
        query["processing_status"] = processing_status.upper()

    if source_id:
        source_object_id = get_object_id(
            source_id,
            "source",
        )
        query["source_id"] = source_object_id

    cursor = raw_observations_collection.find(query).sort(
        "_id",
        -1,
    )

    return await cursor.to_list(length=None)