from datetime import datetime, timezone
from typing import Optional

from app.services.cache import cache
from app.database import locations
from app.database import price_observations
from app.database import product_variants
from app.database import products
from app.utils import get_object_id


ACTIVE = "ACTIVE"
FLAGGED = "FLAGGED"
REJECTED = "REJECTED"

DEFAULT_CURRENCY = "NGN"

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

VALID_FEEDBACK_TYPES = {
    "useful",
    "not_useful",
    "report",
}


class PriceServiceError(Exception):
    pass


class InvalidPriceObservationError(PriceServiceError):
    pass


class PriceObservationNotFoundError(PriceServiceError):
    pass


class PriceProductNotFoundError(PriceServiceError):
    pass


class PriceVariantNotFoundError(PriceServiceError):
    pass


class PriceLocationNotFoundError(PriceServiceError):
    pass


def _invalidate_price_caches():
    cache.delete_prefix("search:")
    cache.delete_prefix("price_analysis:")
    
def _now():
    
    return datetime.now(timezone.utc)


def _validate_price(price: int) -> int:
    if not isinstance(price, int):
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
            "Observed date must be a datetime."
        )

    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(
            tzinfo=timezone.utc
        )

    if observed_at > _now():
        raise InvalidPriceObservationError(
            "Observed date cannot be in the future."
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
            "Invalid seller type."
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


def _optional_object_id(
    value: Optional[str],
    resource: str,
):
    if value is None:
        return None

    if not isinstance(value, str):
        raise InvalidPriceObservationError(
            f"{resource.title()} ID must be a string."
        )

    value = value.strip()

    if not value:
        return None

    try:
        return get_object_id(value, resource)
    except Exception as exc:
        raise InvalidPriceObservationError(
            f"Invalid {resource} ID."
        ) from exc


async def create_price_observation(
    *,
    product_id: str,
    variant_id: str,
    price: int,
    location_id: str,
    observed_at: datetime,
    submitted_by: Optional[str],
    seller_type: Optional[str] = None,
    source_id: Optional[str] = None,
    evidence: Optional[dict] = None,
):
    price = _validate_price(price)
    observed_at = _validate_observed_at(observed_at)
    seller_type = _validate_seller_type(seller_type)
    evidence = _validate_evidence(evidence)

    if not isinstance(product_id, str):
        raise InvalidPriceObservationError(
            "Product ID must be a string."
        )

    if not isinstance(variant_id, str):
        raise InvalidPriceObservationError(
            "Variant ID must be a string."
        )

    if not isinstance(location_id, str):
        raise InvalidPriceObservationError(
            "Location ID must be a string."
        )

    product_id = product_id.strip()
    variant_id = variant_id.strip()
    location_id = location_id.strip()

    if not product_id:
        raise InvalidPriceObservationError(
            "Product ID is required."
        )

    if not variant_id:
        raise InvalidPriceObservationError(
            "Variant ID is required."
        )

    if not location_id:
        raise InvalidPriceObservationError(
            "Location ID is required."
        )

    product = await products.get_product_by_id(
        product_id
    )

    if not product:
        raise PriceProductNotFoundError(
            "Product not found."
        )

    variant = await product_variants.get_variant_by_id(
        variant_id
    )

    if not variant:
        raise PriceVariantNotFoundError(
            "Product variant not found."
        )

    if str(variant["product_id"]) != str(
        product["_id"]
    ):
        raise InvalidPriceObservationError(
            "Product variant does not belong to product."
        )

    location = await locations.get_location_by_id(
        location_id
    )

    if not location:
        raise PriceLocationNotFoundError(
            "Location not found."
        )

    if submitted_by:
        _optional_object_id(
            submitted_by,
            "user",
        )

    if source_id:
        _optional_object_id(
            source_id,
            "source",
        )

    observation = await (
        price_observations.create_price_observation(
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

    if observation is None:
        raise InvalidPriceObservationError(
            "Unable to create price observation."
        )
        
    _invalidate_price_caches()
    
    return observation


async def get_price_observation(
    observation_id: str,
):
    observation = (
        await price_observations
        .get_price_observation_by_id(
            observation_id
        )
    )

    if observation is None:
        raise PriceObservationNotFoundError(
            "Price observation not found."
        )

    return observation


async def get_product_price_observations(
    *,
    product_id: str,
    variant_id: Optional[str] = None,
    location_id: Optional[str] = None,
    status: str = ACTIVE,
):
    observations = await (
        price_observations.get_price_observations(
            product_id=product_id,
            variant_id=variant_id,
            location_id=location_id,
            status=status,
        )
    )

    return observations


async def submit_feedback(
    *,
    observation_id: str,
    feedback_type: str,
):
    if not isinstance(feedback_type, str):
        raise InvalidPriceObservationError(
            "Feedback type must be a string."
        )

    feedback_type = feedback_type.strip().lower()

    if feedback_type not in VALID_FEEDBACK_TYPES:
        raise InvalidPriceObservationError(
            "Invalid feedback type."
        )

    observation = await get_price_observation(
        observation_id
    )

    updated = await (
        price_observations.increment_feedback(
            observation_id,
            feedback_type,
        )
    )

    if updated is None:
        raise PriceObservationNotFoundError(
            "Price observation not found."
        )

    return updated


async def flag_price_observation(
    observation_id: str,
):
    observation = await get_price_observation(
        observation_id
    )

    if observation.get("status") == REJECTED:
        raise InvalidPriceObservationError(
            "Rejected observations cannot be flagged."
        )

    updated_observation = await (
        price_observations
        .update_price_observation_status(
            observation_id,
            FLAGGED,
        )
    )

    if updated_observation is not None:
        _invalidate_price_caches()

    return updated_observation


async def restore_price_observation(
    observation_id: str,
):
    observation = await get_price_observation(
        observation_id
    )

    if observation.get("status") == REJECTED:
        raise InvalidPriceObservationError(
            "Rejected observations cannot be restored."
        )

    updated_observation = await (
        price_observations
        .update_price_observation_status(
            observation_id,
            ACTIVE,
        )
    )

    if updated_observation is not None:
        _invalidate_price_caches()

    return updated_observation


async def reject_price_observation(
    observation_id: str,
):
    await get_price_observation(
        observation_id
    )

    updated_observation = await (
        price_observations
        .update_price_observation_status(
            observation_id,
            REJECTED,
        )
    )

    if updated_observation is not None:
        _invalidate_price_caches()

    return updated_observation