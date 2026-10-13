from datetime import datetime

from app.services import price_observations as price_observations_service


def serialize_price_observation(
    observation: dict,
):
    price = observation.get("price", {})

    return {
        "_id": str(observation["_id"]),
        "product_id": str(observation["product_id"]),
        "variant_id": str(observation["variant_id"]),
        "location_id": str(observation["location_id"]),
        "source_id": (
            str(observation["source_id"])
            if observation.get("source_id")
            else None
        ),
        "submitted_by": (
            str(observation["submitted_by"])
            if observation.get("submitted_by")
            else None
        ),
        "price": {
            "amount": price.get("amount"),
            "currency": price.get("currency"),
        },
        "observed_at": observation.get("observed_at"),
        "seller_type": observation.get("seller_type"),
        "evidence": observation.get("evidence", {}),
        "status": observation.get("status"),
        "feedback": observation.get(
            "feedback",
            {
                "useful": 0,
                "not_useful": 0,
                "reports": 0,
            },
        ),
        "created_at": observation.get("created_at"),
        "updated_at": observation.get("updated_at"),
    }


async def create_price_observation(
    *,
    product_id: str,
    variant_id: str,
    price: int,
    location_id: str,
    observed_at: datetime,
    source_id=None,
    submitted_by=None,
    seller_type=None,
    evidence=None,
):
    observation = (
        await price_observations_service
        .create_price_observation(
            product_id=product_id,
            variant_id=variant_id,
            price=price,
            location_id=location_id,
            observed_at=observed_at,
            source_id=source_id,
            submitted_by=submitted_by,
            seller_type=seller_type,
            evidence=evidence,
        )
    )

    return serialize_price_observation(observation)


async def get_price_observation(
    *,
    observation_id: str,
):
    observation = (
        await price_observations_service
        .get_price_observation(
            observation_id
        )
    )

    return serialize_price_observation(observation)


async def find_price_observations(
    *,
    product_id=None,
    variant_id=None,
    location_id=None,
    source_id=None,
    submitted_by=None,
    seller_type=None,
    status=None,
    limit=50,
    skip=0,
):
    observations = (
        await price_observations_service
        .find_price_observations(
            product_id=product_id,
            variant_id=variant_id,
            location_id=location_id,
            source_id=source_id,
            submitted_by=submitted_by,
            seller_type=seller_type,
            status=status,
            limit=limit,
            skip=skip,
        )
    )

    return [
        serialize_price_observation(observation)
        for observation in observations
    ]


async def get_product_price_observations(
    *,
    product_id: str,
    limit: int = 50,
):
    observations = (
        await price_observations_service
        .get_product_price_observations(
            product_id,
            limit=limit,
        )
    )

    return [
        serialize_price_observation(observation)
        for observation in observations
    ]


async def get_location_price_observations(
    *,
    location_id: str,
    limit: int = 50,
):
    observations = (
        await price_observations_service
        .get_location_price_observations(
            location_id,
            limit=limit,
        )
    )

    return [
        serialize_price_observation(observation)
        for observation in observations
    ]


async def get_user_price_observations(
    *,
    user_id: str,
    limit: int = 50,
):
    observations = (
        await price_observations_service
        .get_user_price_observations(
            user_id,
            limit=limit,
        )
    )

    return [
        serialize_price_observation(observation)
        for observation in observations
    ]


async def update_price_observation(
    *,
    observation_id: str,
    updates: dict,
):
    observation = (
        await price_observations_service
        .update_price_observation(
            observation_id,
            updates,
        )
    )

    return serialize_price_observation(observation)


async def update_price_observation_status(
    *,
    observation_id: str,
    status: str,
):
    observation = (
        await price_observations_service
        .update_price_observation_status(
            observation_id,
            status,
        )
    )

    return serialize_price_observation(observation)