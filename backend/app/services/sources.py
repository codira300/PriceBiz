from typing import Optional

from urllib.parse import urlparse

from app.database import sources as sources_db

from app.services.cache import cache


MAX_SOURCE_NAME_LENGTH = 200
MAX_SOURCE_TYPE_LENGTH = 50
MAX_SOURCE_URL_LENGTH = 2048
SOURCE_CACHE_TTL = 1800

VALID_SOURCE_TYPES = {
    "USER",
    "ADMIN",
    "BUSINESS",
    "MARKET",
    "API",
    "WEBSITE",
    "SOCIAL_MEDIA",
    "SPREADSHEET",
    "OTHER",
}


class SourceServiceError(Exception):
    pass


class InvalidSourceError(SourceServiceError):
    pass


class SourceNotFoundError(SourceServiceError):
    pass


def _validate_required_string(
    value: str,
    field_name: str,
    max_length: int,
) -> str:
    if not isinstance(value, str):
        raise InvalidSourceError(
            f"{field_name} must be a string"
        )

    value = value.strip()

    if not value:
        raise InvalidSourceError(
            f"{field_name} cannot be empty"
        )

    if len(value) > max_length:
        raise InvalidSourceError(
            f"{field_name} cannot exceed "
            f"{max_length} characters"
        )

    return value


def _validate_source_name(
    name: str,
) -> str:
    return _validate_required_string(
        name,
        "Source name",
        MAX_SOURCE_NAME_LENGTH,
    )


def _validate_source_type(
    source_type: str,
) -> str:
    source_type = _validate_required_string(
        source_type,
        "Source type",
        MAX_SOURCE_TYPE_LENGTH,
    )

    source_type = source_type.upper()

    if source_type not in VALID_SOURCE_TYPES:
        raise InvalidSourceError(
            f"Unsupported source type: {source_type}"
        )

    return source_type


def _validate_url(
    url: Optional[str],
) -> Optional[str]:
    if url is None:
        return None

    if not isinstance(url, str):
        raise InvalidSourceError(
            "Source URL must be a string"
        )

    url = url.strip()

    if not url:
        return None

    if len(url) > MAX_SOURCE_URL_LENGTH:
        raise InvalidSourceError(
            f"Source URL cannot exceed "
            f"{MAX_SOURCE_URL_LENGTH} characters"
        )

    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise InvalidSourceError(
            "Source URL must use http or https"
        )

    if not parsed.netloc:
        raise InvalidSourceError(
            "Source URL must contain a valid host"
        )

    return url


def _validate_metadata(
    metadata: Optional[dict],
) -> dict:
    if metadata is None:
        return {}

    if not isinstance(metadata, dict):
        raise InvalidSourceError(
            "Source metadata must be an object"
        )

    return metadata


async def _ensure_source_does_not_exist(
    *,
    name: str,
    source_type: str,
    exclude_source_id: Optional[str] = None,
):
    source = await sources_db.get_source_by_name_and_type(
        name=name,
        source_type=source_type,
    )

    if source is None:
        return

    if (
        exclude_source_id is not None
        and str(source["_id"]) == exclude_source_id
    ):
        return

    raise InvalidSourceError(
        "A source with this name and type already exists"
    )


async def create_source(
    *,
    name: str,
    source_type: str,
    url: Optional[str] = None,
    metadata: Optional[dict] = None,
):
    name = _validate_source_name(name)

    source_type = _validate_source_type(
        source_type
    )

    url = _validate_url(url)

    metadata = _validate_metadata(
        metadata
    )

    await _ensure_source_does_not_exist(
        name=name,
        source_type=source_type,
    )
    
    source = await sources_db.create_source(
        name=name,
        source_type=source_type,
        url=url,
        metadata=metadata,
    )

    cache.delete_prefix("sources:")

    return source


async def get_source(
    source_id: str,
):
    if not isinstance(source_id, str):
        raise InvalidSourceError(
            "Source ID must be a string"
        )

    source_id = source_id.strip()

    if not source_id:
        raise InvalidSourceError(
            "Source ID cannot be empty"
        )

    cache_key = f"source:{source_id}"
    
    cached = cache.get(cache_key)
    
    if cached is not None:
        return cached
    
    source = await sources_db.get_source_by_id(
        source_id
    )

    if source is None:
        raise SourceNotFoundError(
            "Source not found"
        )
        
    cache.set(
        cache_key,
        source,
        SOURCE_CACHE_TTL,
    )
    
    return source


async def find_sources(
    *,
    source_type: Optional[str] = None,
    name: Optional[str] = None,
):
    if source_type is not None:
        source_type = _validate_source_type(
            source_type
        )

    if name is not None:
        name = _validate_source_name(
            name
        )
        
    cache_key = (
    "sources:"
    f"{source_type or ''}:"
    f"{name or ''}"
)

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    sources = await sources_db.find_sources(
    source_type=source_type,
    name=name,
)

    cache.set(
        cache_key,
        sources,
        SOURCE_CACHE_TTL,
    )

    return sources


async def update_source(
    *,
    source_id: str,
    name: Optional[str] = None,
    source_type: Optional[str] = None,
    url: Optional[str] = None,
    metadata: Optional[dict] = None,
):
    if not isinstance(source_id, str):
        raise InvalidSourceError(
            "Source ID must be a string"
        )

    source_id = source_id.strip()

    if not source_id:
        raise InvalidSourceError(
            "Source ID cannot be empty"
        )

    current = await sources_db.get_source_by_id(
        source_id
    )

    if current is None:
        raise SourceNotFoundError(
            "Source not found"
        )

    updates = {}

    if name is not None:
        updates["name"] = _validate_source_name(
            name
        )

    if source_type is not None:
        updates["type"] = _validate_source_type(
            source_type
        )

    if url is not None:
        updates["url"] = _validate_url(url)

    if metadata is not None:
        updates["metadata"] = _validate_metadata(
            metadata
        )

    if not updates:
        raise InvalidSourceError(
            "At least one source field must be "
            "provided for update"
        )

    merged = {
        "name": current["name"],
        "type": current["type"],
        "url": current.get("url"),
        "metadata": current.get("metadata", {}),
        **updates,
    }

    await _ensure_source_does_not_exist(
        name=merged["name"],
        source_type=merged["type"],
        exclude_source_id=source_id,
    )

    updated_source = await sources_db.update_source(
        source_id,
        updates,
    )

    if updated_source is None:
        raise SourceNotFoundError(
            "Source not found"
        )

    cache.delete(
        f"source:{source_id}"
    )

    cache.delete_prefix("sources:")

    return updated_source