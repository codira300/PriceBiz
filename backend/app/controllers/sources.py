from typing import Optional, Any

from app.services import sources as sources_service


def serialize_source(source: dict):
    return {
        "_id": str(source["_id"]),
        "name": source.get("name"),
        "type": source.get("type"),
        "url": source.get("url"),
        "metadata": source.get("metadata", {}),
    }


async def create_source(
    *,
    name: str,
    source_type: str,
    url: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
):
    source = await sources_service.create_source(
        name=name,
        source_type=source_type,
        url=url,
        metadata=metadata,
    )

    return serialize_source(source)


async def get_source(
    *,
    source_id: str,
):
    source = await sources_service.get_source(
        source_id=source_id,
    )

    return serialize_source(source)


async def find_sources(
    *,
    source_type: Optional[str] = None,
    name: Optional[str] = None,
):
    sources = await sources_service.find_sources(
        source_type=source_type,
        name=name,
    )

    return [
        serialize_source(source)
        for source in sources
    ]


async def update_source(
    *,
    source_id: str,
    name: Optional[str] = None,
    source_type: Optional[str] = None,
    url: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
):
    source = await sources_service.update_source(
        source_id=source_id,
        name=name,
        source_type=source_type,
        url=url,
        metadata=metadata,
    )

    return serialize_source(source)