from typing import Optional

from app.services import locations as locations_service


def serialize_location(location: dict):
    return {
        "_id": str(location["_id"]),
        "country": location.get("country"),
        "state": location.get("state"),
        "lga": location.get("lga"),
        "area": location.get("area"),
        "market": location.get("market"),
    }


async def create_location(
    *,
    country: str,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    location = await locations_service.create_location(
        country=country,
        state=state,
        lga=lga,
        area=area,
        market=market,
    )

    return serialize_location(location)


async def get_location(
    *,
    location_id: str,
):
    location = await locations_service.get_location(
        location_id=location_id,
    )

    return serialize_location(location)


async def find_locations(
    *,
    country: Optional[str] = None,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    locations = await locations_service.find_locations(
        country=country,
        state=state,
        lga=lga,
        area=area,
        market=market,
    )

    return [
        serialize_location(location)
        for location in locations
    ]


async def update_location(
    *,
    location_id: str,
    country: Optional[str] = None,
    state: Optional[str] = None,
    lga: Optional[str] = None,
    area: Optional[str] = None,
    market: Optional[str] = None,
):
    location = await locations_service.update_location(
        location_id=location_id,
        country=country,
        state=state,
        lga=lga,
        area=area,
        market=market,
    )

    return serialize_location(location)