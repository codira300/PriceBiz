from typing import Optional
import re
from app.database.connection import database
from app.database.validation import SourceData
from app.utils import get_object_id


sources_collection = database.sources


async def create_source(
    name: str,
    source_type: str,
    url: Optional[str] = None,
    metadata: Optional[dict] = None,
):
    source_data = SourceData(
        name=name,
        type=source_type,
        url=url,
        metadata=metadata or {},
    )

    result = await sources_collection.insert_one(
        source_data.model_dump()
    )

    return await sources_collection.find_one(
        {"_id": result.inserted_id}
    )


async def get_source_by_id(source_id: str):
    source_object_id = get_object_id(
        source_id,
        "source",
    )

    return await sources_collection.find_one(
        {"_id": source_object_id}
    )
    
async def get_source_by_name(name: str):
    return await sources_collection.find_one(
        {
            "name": {
                "$regex": f"^{re.escape(name)}$",
                "$options": "i",
            }
        }
    ) 


async def find_sources(
    source_type: Optional[str] = None,
    name: Optional[str] = None,
):
    query = {}

    if source_type:
        query["type"] = source_type

    if name:
        query["name"] = {
            "$regex": name,
            "$options": "i",
        }

    cursor = sources_collection.find(query)

    return await cursor.to_list(length=None)


async def update_source(
    source_id: str,
    updates: dict,
):
    source_object_id = get_object_id(
        source_id,
        "source",
    )

    current = await sources_collection.find_one(
        {"_id": source_object_id}
    )

    if current is None:
        return None

    current.pop("_id", None)

    merged = {
        **current,
        **updates,
    }

    validated = SourceData(**merged)

    await sources_collection.update_one(
        {"_id": source_object_id},
        {
            "$set": validated.model_dump()
        },
    )

    return await get_source_by_id(source_id)


async def get_source_by_name_and_type(
    name: str,
    source_type: str,
):
    return await sources_collection.find_one(
        {
            "name": {
                "$regex": f"^{name}$",
                "$options": "i",
            },
            "type": source_type,
        }
    )