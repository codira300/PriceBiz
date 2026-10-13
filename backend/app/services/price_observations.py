from datetime import datetime, timezone
from typing import Optional
from app.services.cache import cache
from app.database import price_observations as price_observations_db
from app.utils import get_object_id


VALID_SELLER_TYPES = {
    "STORE",
    "SHOP",
    "MINI_FARM",
    "MARKET",
    "SUPERMARKET",
    "WHOLESALER",
    "ONLINE",
    "OTHER",
}

VALID_STATUSES = {
    "ACTIVE",
    "FLAGGED",
    "REJECTED",
    "EXPIRED",
}


class PriceObservationServiceError(Exception):
    pass


class InvalidPriceObservationError(PriceObservationServiceError):
    pass


class PriceObservationNotFoundError(PriceObservationServiceError):
    pass


class DuplicatePriceObservationError(PriceObservationServiceError):
    pass


def _invalidate_price_caches():
    cache.delete_prefix("search:")
    cache.delete_prefix("price_analysis:")
    
    
def _validate_id(
    value: str,
    resource: str,
) -> str:
    if not isinstance(value, str):
        raise InvalidPriceObservationError(
            f"{resource.capitalize()} ID must be a string."
        )

    value = value.strip()

    if not value:
        raise InvalidPriceObservationError(
            f"{resource.capitalize()} ID is required."
        )

    try:
        get_object_id(value, resource)
    except Exception as exc:
        raise InvalidPriceObservationError(
            f"Invalid {resource} ID."
        ) from exc

    return value


def _validate_price(price: int) -> int:
    if isinstance(price, bool) or not isinstance(price, int):
        raise InvalidPriceObservationError(
            "Price must be an integer."
        )

    if price <= 0:
        raise InvalidPriceObservationError(
            "Price must be greater than zero."
        )

    return price


def _validate_observed_at(
    observed_at: datetime,
) -> datetime:
    if not isinstance(observed_at, datetime):
        raise InvalidPriceObservationError(
            "observed_at must be a valid datetime."
        )

    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(
            tzinfo=timezone.utc
        )

    return observed_at


def _validate_seller_type(
    seller_type: Optional[str],
) -> Optional[str]:
    if seller_type is None:
        return None

    if not isinstance(seller_type, str):
        raise InvalidPriceObservationError(
            "Seller type must be a string."
        )

    seller_type = seller_type.strip().upper()

    if not seller_type:
        return None

    if seller_type not in VALID_SELLER_TYPES:
        raise InvalidPriceObservationError(
            f"Unsupported seller type: {seller_type}"
        )

    return seller_type


def _validate_evidence(
    evidence: Optional[dict],
) -> dict:
    if evidence is None:
        return {}

    if not isinstance(evidence, dict):
        raise InvalidPriceObservationError(
            "Evidence must be an object."
        )

    return evidence


def _validate_status(status: str) -> str:
    if not isinstance(status, str):
        raise InvalidPriceObservationError(
            "Status must be a string."
        )

    status = status.strip().upper()

    if status not in VALID_STATUSES:
        raise InvalidPriceObservationError(
            f"Unsupported price observation status: {status}"
        )

    return status


async def create_price_observation(
    *,
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
    product_id = _validate_id(
        product_id,
        "product",
    )

    variant_id = _validate_id(
        variant_id,
        "product variant",
    )

    location_id = _validate_id(
        location_id,
        "location",
    )

    if source_id is not None:
        source_id = _validate_id(
            source_id,
            "source",
        )

    if submitted_by is not None:
        submitted_by = _validate_id(
            submitted_by,
            "user",
        )

    price = _validate_price(price)

    observed_at = _validate_observed_at(
        observed_at
    )

    seller_type = _validate_seller_type(
        seller_type
    )

    evidence = _validate_evidence(
        evidence
    )

    try:
        observation = (
            await price_observations_db
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
    except ValueError as exc:
        raise InvalidPriceObservationError(
            str(exc)
        ) from exc

    if observation is None:
        raise InvalidPriceObservationError(
            "Unable to create price observation. "
            "One or more referenced resources do not exist."
        )

    _invalidate_price_caches()

    return observation


async def get_price_observation(
    observation_id: str,
):
    observation_id = _validate_id(
        observation_id,
        "price observation",
    )

    observation = (
        await price_observations_db
        .get_price_observation_by_id(
            observation_id
        )
    )

    if observation is None:
        raise PriceObservationNotFoundError(
            "Price observation not found."
        )

    return observation


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
    if product_id is not None:
        product_id = _validate_id(
            product_id,
            "product",
        )

    if variant_id is not None:
        variant_id = _validate_id(
            variant_id,
            "product variant",
        )

    if location_id is not None:
        location_id = _validate_id(
            location_id,
            "location",
        )

    if source_id is not None:
        source_id = _validate_id(
            source_id,
            "source",
        )

    if submitted_by is not None:
        submitted_by = _validate_id(
            submitted_by,
            "user",
        )

    seller_type = _validate_seller_type(
        seller_type
    )

    if status is not None:
        status = _validate_status(status)

    if not isinstance(limit, int) or isinstance(limit, bool):
        raise InvalidPriceObservationError(
            "Limit must be an integer."
        )

    if limit < 1:
        raise InvalidPriceObservationError(
            "Limit must be greater than zero."
        )

    if limit > 100:
        raise InvalidPriceObservationError(
            "Limit cannot exceed 100."
        )

    if not isinstance(skip, int) or isinstance(skip, bool):
        raise InvalidPriceObservationError(
            "Skip must be an integer."
        )

    if skip < 0:
        raise InvalidPriceObservationError(
            "Skip cannot be negative."
        )

    return await price_observations_db.find_price_observations(
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


async def get_product_price_observations(
    product_id: str,
    limit: int = 50,
):
    product_id = _validate_id(
        product_id,
        "product",
    )

    if limit < 1 or limit > 100:
        raise InvalidPriceObservationError(
            "Limit must be between 1 and 100."
        )

    return await (
        price_observations_db
        .get_price_observations_by_product(
            product_id,
            limit=limit,
        )
    )


async def get_location_price_observations(
    location_id: str,
    limit: int = 50,
):
    location_id = _validate_id(
        location_id,
        "location",
    )

    if limit < 1 or limit > 100:
        raise InvalidPriceObservationError(
            "Limit must be between 1 and 100."
        )

    return await (
        price_observations_db
        .get_price_observations_by_location(
            location_id,
            limit=limit,
        )
    )


async def get_user_price_observations(
    user_id: str,
    limit: int = 50,
):
    user_id = _validate_id(
        user_id,
        "user",
    )

    if limit < 1 or limit > 100:
        raise InvalidPriceObservationError(
            "Limit must be between 1 and 100."
        )

    return await (
        price_observations_db
        .get_price_observations_by_user(
            user_id,
            limit=limit,
        )
    )


async def update_price_observation(
    observation_id: str,
    updates: dict,
):
    observation_id = _validate_id(
        observation_id,
        "price observation",
    )

    if not isinstance(updates, dict):
        raise InvalidPriceObservationError(
            "Updates must be an object."
        )

    if not updates:
        raise InvalidPriceObservationError(
            "No updates provided."
        )

    allowed_fields = {
        "price",
        "observed_at",
        "seller_type",
        "evidence",
    }

    invalid_fields = set(updates) - allowed_fields

    if invalid_fields:
        raise InvalidPriceObservationError(
            "Unsupported update fields: "
            + ", ".join(sorted(invalid_fields))
        )

    validated_updates = {}

    if "price" in updates:
        validated_updates["price"] = _validate_price(
            updates["price"]
        )

    if "observed_at" in updates:
        validated_updates["observed_at"] = (
            _validate_observed_at(
                updates["observed_at"]
            )
        )

    if "seller_type" in updates:
        validated_updates["seller_type"] = (
            _validate_seller_type(
                updates["seller_type"]
            )
        )

    if "evidence" in updates:
        validated_updates["evidence"] = (
            _validate_evidence(
                updates["evidence"]
            )
        )

    try:
        observation = (
            await price_observations_db
            .update_price_observation(
                observation_id,
                validated_updates,
            )
        )
    except ValueError as exc:
        raise InvalidPriceObservationError(
            str(exc)
        ) from exc

    if observation is None:
        raise PriceObservationNotFoundError(
            "Price observation not found."
        )

    _invalidate_price_caches()

    return observation


async def update_price_observation_status(
    observation_id: str,
    status: str,
):
    observation_id = _validate_id(
        observation_id,
        "price observation",
    )

    status = _validate_status(status)

    observation = (
        await price_observations_db
        .update_price_observation_status(
            observation_id,
            status,
        )
    )

    if observation is None:
        raise PriceObservationNotFoundError(
            "Price observation not found."
        )

    _invalidate_price_caches()

    return observation