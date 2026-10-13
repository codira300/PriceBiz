from typing import Optional
from app.services.cache import cache
from app.database import locations as locations_db
from app.config import (
    LOCATION_CACHE_TTL,
    MAX_COUNTRY_LENGTH,
    MAX_STATE_LENGTH,
    MAX_LGA_LENGTH,
    MAX_AREA_LENGTH, 
    MAX_MARKET_LENGTH 
)


class LocationServiceError(Exception):
    pass


class InvalidLocationError(LocationServiceError):
    pass


class LocationNotFoundError(LocationServiceError):
    pass


def _validate_location_value(
    value: Optional[str],
    field_name: str,
    max_length: int,
    required: bool = False,
) -> Optional[str]:
    if value is None:
        if required:
            raise InvalidLocationError(
                f"{field_name} is required"
            )
        return None

    if not isinstance(value, str):
        raise InvalidLocationError(
            f"{field_name} must be a string"
        )

    value = value.strip()

    if not value:
        if required:
            raise InvalidLocationError(
                f"{field_name} cannot be empty"
            )

        return None

    if len(value) > max_length:
        raise InvalidLocationError(
            f"{field_name} cannot exceed "
            f"{max_length} characters"
        )

    return value


def _validate_location_fields(
    country: str,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    return {
        "country": _validate_location_value(
            country,
            "Country",
            MAX_COUNTRY_LENGTH,
            required=True,
        ),
        "state": _validate_location_value(
            state,
            "State",
            MAX_STATE_LENGTH,
        ),
        "lga": _validate_location_value(
            lga,
            "LGA",
            MAX_LGA_LENGTH,
        ),
        "area": _validate_location_value(
            area,
            "Area",
            MAX_AREA_LENGTH,
        ),
        "market": _validate_location_value(
            market,
            "Market",
            MAX_MARKET_LENGTH,
        ),
    }


async def _ensure_location_does_not_exist(
    *,
    country: str,
    state: Optional[str],
    lga: Optional[str],
    area: Optional[str],
    market: Optional[str],
    exclude_location_id: Optional[str] = None,
):
    locations = await locations_db.find_locations(
        country=country,
        state=state,
        lga=lga,
        area=area,
        market=market,
    )

    if not locations:
        return

    if exclude_location_id is None:
        raise InvalidLocationError(
            "This location already exists"
        )

    for location in locations:
        if str(location["_id"]) != exclude_location_id:
            raise InvalidLocationError(
                "This location already exists"
            )


async def create_location(
    *,
    country: str,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    validated = _validate_location_fields(
        country=country,
        state=state,
        lga=lga,
        area=area,
        market=market,
    )

    await _ensure_location_does_not_exist(
        **validated
    )

    location = await locations_db.create_location(
    **validated
    )

    cache.delete_prefix("locations:")
    cache.delete_prefix("price_analysis:")

    return location


async def get_location(
    location_id: str,
):
    if not isinstance(location_id, str):
        raise InvalidLocationError(
            "Location ID must be a string"
        )

    location_id = location_id.strip()

    if not location_id:
        raise InvalidLocationError(
            "Location ID cannot be empty"
        )

    cache_key = f"location:{location_id}"

    cached = cache.get(cache_key)

    if cached is not None:
        return cached
    
    location = await locations_db.get_location_by_id(
        location_id
    )

    if location is None:
        raise LocationNotFoundError(
            "Location not found"
        )

    cache.set(
            cache_key,
            location,
            LOCATION_CACHE_TTL,
        )
    
    return location

async def find_locations(
    *,
    country: Optional[str] = None,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    if country is not None:
        country = _validate_location_value(
            country,
            "Country",
            MAX_COUNTRY_LENGTH,
        )

    if state is not None:
        state = _validate_location_value(
            state,
            "State",
            MAX_STATE_LENGTH,
        )

    if lga is not None:
        lga = _validate_location_value(
            lga,
            "LGA",
            MAX_LGA_LENGTH,
        )

    if area is not None:
        area = _validate_location_value(
            area,
            "Area",
            MAX_AREA_LENGTH,
        )

    if market is not None:
        market = _validate_location_value(
            market,
            "Market",
            MAX_MARKET_LENGTH,
        )

    cache_key = (
        "locations:"
        f"{country or ''}:"
        f"{state or ''}:"
        f"{lga or ''}:"
        f"{area or ''}:"
        f"{market or ''}"
    )

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    locations = await locations_db.find_locations(
        country=country,
        state=state,
        lga=lga,
        area=area,
        market=market,
    )

    cache.set(
        cache_key,
        locations,
        LOCATION_CACHE_TTL,
    )

    return locations


async def update_location(
    *,
    location_id: str,
    country: Optional[str] = None,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    if not isinstance(location_id, str):
        raise InvalidLocationError(
            "Location ID must be a string"
        )

    location_id = location_id.strip()

    if not location_id:
        raise InvalidLocationError(
            "Location ID cannot be empty"
        )

    current = await locations_db.get_location_by_id(
        location_id
    )

    if current is None:
        raise LocationNotFoundError(
            "Location not found"
        )

    updates = {}

    if country is not None:
        updates["country"] = _validate_location_value(
            country,
            "Country",
            MAX_COUNTRY_LENGTH,
            required=True,
        )

    if state is not None:
        updates["state"] = _validate_location_value(
            state,
            "State",
            MAX_STATE_LENGTH,
        )

    if lga is not None:
        updates["lga"] = _validate_location_value(
            lga,
            "LGA",
            MAX_LGA_LENGTH,
        )

    if area is not None:
        updates["area"] = _validate_location_value(
            area,
            "Area",
            MAX_AREA_LENGTH,
        )

    if market is not None:
        updates["market"] = _validate_location_value(
            market,
            "Market",
            MAX_MARKET_LENGTH,
        )

    if not updates:
        raise InvalidLocationError(
            "At least one location field must be provided "
            "for update"
        )

    merged = {
        "country": current["country"],
        "state": current.get("state"),
        "lga": current.get("lga"),
        "area": current.get("area"),
        "market": current.get("market"),
        **updates,
    }

    await _ensure_location_does_not_exist(
        **merged,
        exclude_location_id=location_id,
    )

    updated_location = await locations_db.update_location(
        location_id,
        updates,
    )

    if updated_location is None:
        raise LocationNotFoundError(
            "Location not found"
        )
    
    cache.delete(
    f"location:{location_id}"
    )
    cache.delete_prefix("locations:")
    cache.delete_prefix("price_analysis:")

    return updated_location