from datetime import datetime, timezone
from typing import Any, Optional

from app.database import locations as locations_db
from app.database import product_variants as product_variants_db
from app.database import products as products_db
from app.database import raw_observations as raw_observations_db
from app.database import sources as sources_db
from app.services.price_observations import create_price_observation
from app.queue import task_queue


PENDING = "PENDING"
PROCESSING = "PROCESSING"
PROCESSED = "PROCESSED"
REJECTED = "REJECTED"
FAILED = "FAILED"


VALID_PROCESSING_STATUSES = {
    PENDING,
    PROCESSING,
    PROCESSED,
    REJECTED,
    FAILED,
}


SUPPORTED_INPUT_FORMATS = {
    "SEED_SPREADSHEET_V1",
}


class RawObservationProcessingError(Exception):
    pass


class InvalidRawObservationError(
    RawObservationProcessingError
):
    pass


class RawObservationNotFoundError(
    RawObservationProcessingError
):
    pass


class UnsupportedInputFormatError(
    RawObservationProcessingError
):
    pass


class RawObservationProcessingFailedError(
    RawObservationProcessingError
):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_required_string(
    value: Any,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise InvalidRawObservationError(
            f"{field_name} must be a string."
        )

    value = value.strip()

    if not value:
        raise InvalidRawObservationError(
            f"{field_name} is required."
        )

    return value


def _normalize_input_format(
    input_format: str,
) -> str:
    input_format = _validate_required_string(
        input_format,
        "Input format",
    )

    input_format = input_format.upper()

    if input_format not in SUPPORTED_INPUT_FORMATS:
        raise UnsupportedInputFormatError(
            f"Unsupported input format: {input_format}"
        )

    return input_format


def _validate_processing_status(
    processing_status: str,
) -> str:
    processing_status = _validate_required_string(
        processing_status,
        "Processing status",
    )

    processing_status = processing_status.upper()

    if processing_status not in VALID_PROCESSING_STATUSES:
        raise InvalidRawObservationError(
            f"Invalid processing status: "
            f"{processing_status}"
        )

    return processing_status


def _get_payload_value(
    payload: dict,
    *keys: str,
):
    for key in keys:
        if key not in payload:
            continue

        value = payload[key]

        if value is None:
            continue

        if isinstance(value, str):
            if not value.strip():
                continue

            return value.strip()

        return value

    return None


def _parse_price(
    value: Any,
) -> int:
    if value is None:
        raise InvalidRawObservationError(
            "Price is required."
        )

    if isinstance(value, bool):
        raise InvalidRawObservationError(
            "Price must be a valid number."
        )

    if isinstance(value, (int, float)):
        price = float(value)

    elif isinstance(value, str):
        cleaned = (
            value.strip()
            .replace("₦", "")
            .replace("NGN", "")
            .replace("ngn", "")
            .replace(",", "")
            .strip()
        )

        if not cleaned:
            raise InvalidRawObservationError(
                "Price is required."
            )

        try:
            price = float(cleaned)
        except ValueError as exc:
            raise InvalidRawObservationError(
                f"Invalid price: {value}"
            ) from exc

    else:
        raise InvalidRawObservationError(
            "Invalid price value."
        )

    if price <= 0:
        raise InvalidRawObservationError(
            "Price must be greater than zero."
        )

    if not price.is_integer():
        raise InvalidRawObservationError(
            "Price must be a whole NGN amount."
        )

    return int(price)


def _parse_observed_at(
    value: Any,
) -> datetime:
    if value is None:
        raise InvalidRawObservationError(
            "Observed date is required."
        )

    if isinstance(value, datetime):
        observed_at = value

    elif isinstance(value, str):
        value = value.strip()

        if not value:
            raise InvalidRawObservationError(
                "Observed date is required."
            )

        try:
            observed_at = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise InvalidRawObservationError(
                f"Invalid observed date: {value}"
            ) from exc

    else:
        raise InvalidRawObservationError(
            "Invalid observed date."
        )

    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(
            tzinfo=timezone.utc
        )
    else:
        observed_at = observed_at.astimezone(
            timezone.utc
        )

    if observed_at > _now():
        raise InvalidRawObservationError(
            "Observed date cannot be in the future."
        )

    return observed_at


def _parse_location(
    value: Any,
) -> dict:
    if isinstance(value, dict):
        location = {}

        for key in (
            "country",
            "state",
            "lga",
            "area",
            "market",
        ):
            field_value = value.get(key)

            if field_value is None:
                continue

            if isinstance(field_value, str):
                field_value = field_value.strip()

            if field_value:
                location[key] = str(field_value).strip()

        if not location:
            raise InvalidRawObservationError(
                "Location cannot be empty."
            )

        if not location.get("country"):
            raise InvalidRawObservationError(
                "Location country is required."
            )

        return location

    if not isinstance(value, str):
        raise InvalidRawObservationError(
            "Location must be a string or object."
        )

    parts = [
        part.strip()
        for part in value.split(",")
        if part.strip()
    ]

    if not parts:
        raise InvalidRawObservationError(
            "Location cannot be empty."
        )

    if len(parts) == 1:
        return {
            "country": "Nigeria",
            "lga": parts[0],
        }

    if len(parts) == 2:
        return {
            "country": "Nigeria",
            "state": parts[1],
            "lga": parts[0],
        }

 
    if len(parts) == 3:
        return {
            "country": parts[2],
            "state": parts[1],
            "lga": parts[0],
        }

   
    if len(parts) == 4:
        return {
            "country": parts[3],
            "state": parts[2],
            "lga": parts[1],
            "area": parts[0],
        }

    
    return {
        "country": parts[-1],
        "state": parts[-2],
        "lga": parts[-3],
        "area": parts[-4],
        "market": parts[-5],
    }


def _parse_seller_type(
    value: Any,
) -> Optional[str]:
    if value is None:
        return None

    if not isinstance(value, str):
        raise InvalidRawObservationError(
            "Seller type must be a string."
        )

    value = value.strip().upper()

    if not value:
        return None

    return value


def _build_variant_name(
    payload: dict,
) -> str:
    variant = _get_payload_value(
        payload,
        "Variant",
        "variant",
        "Variant Name",
        "variant_name",
        "Size",
        "size",
    )

    if variant is not None:
        variant_name = str(variant).strip()

        if variant_name:
            return variant_name

    quantity = _get_payload_value(
        payload,
        "Quantity",
        "quantity",
    )

    unit = _get_payload_value(
        payload,
        "Unit",
        "unit",
    )

    if quantity is not None:
        quantity = str(quantity).strip()

        if unit is not None:
            unit = str(unit).strip()

        if quantity and unit:
            return f"{quantity} {unit}"

        if quantity:
            return quantity

    raise InvalidRawObservationError(
        "Variant name, size, or quantity is required."
    )


def _build_variant_attributes(
    payload: dict,
) -> dict:
    attributes = {}

    size = _get_payload_value(
        payload,
        "Size",
        "size",
    )

    if size is not None:
        attributes["size"] = str(size).strip()

    unit = _get_payload_value(
        payload,
        "Unit",
        "unit",
    )

    if unit is not None:
        attributes["unit"] = str(unit).strip()

    quantity = _get_payload_value(
        payload,
        "Quantity",
        "quantity",
    )

    if quantity is not None:
        attributes["quantity"] = str(
            quantity
        ).strip()

    return attributes


def _map_seed_spreadsheet_v1(
    payload: dict,
) -> dict:
    product_name = _get_payload_value(
        payload,
        "Product",
        "product",
        "Product Name",
        "product_name",
    )

    brand = _get_payload_value(
        payload,
        "Brand",
        "brand",
    )

    price = _get_payload_value(
        payload,
        "Price ₦",
        "Price",
        "price",
        "price_ngn",
    )

    location = _get_payload_value(
        payload,
        "Location",
        "location",
    )

    observed_at = _get_payload_value(
        payload,
        "Observed At",
        "observed_at",
        "Date",
        "date",
    )

    seller_type = _get_payload_value(
        payload,
        "Seller Type",
        "seller_type",
    )

    source = _get_payload_value(
        payload,
        "Source",
        "source",
    )

    if product_name is None:
        raise InvalidRawObservationError(
            "Product name is missing from payload."
        )

    if price is None:
        raise InvalidRawObservationError(
            "Price is missing from payload."
        )

    if location is None:
        raise InvalidRawObservationError(
            "Location is missing from payload."
        )

    return {
        "product_name": str(
            product_name
        ).strip(),

        "brand": (
            str(brand).strip()
            if brand is not None
            else None
        ),

        "price": _parse_price(price),

        "location": _parse_location(
            location
        ),

        "observed_at": _parse_observed_at(
            observed_at
        ),

        "seller_type": _parse_seller_type(
            seller_type
        ),

        "source": (
            str(source).strip()
            if source is not None
            else None
        ),

        "variant_name": _build_variant_name(
            payload
        ),

        "variant_attributes": (
            _build_variant_attributes(
                payload
            )
        ),
    }


def _map_payload(
    input_format: str,
    payload: dict,
) -> dict:
    if not isinstance(payload, dict):
        raise InvalidRawObservationError(
            "Payload must be an object."
        )

    input_format = _normalize_input_format(
        input_format
    )

    if input_format == "SEED_SPREADSHEET_V1":
        return _map_seed_spreadsheet_v1(
            payload
        )

    raise UnsupportedInputFormatError(
        f"Unsupported input format: {input_format}"
    )


async def _resolve_location(
    location_data: dict,
):
    location = await locations_db.find_locations(
        country=location_data.get("country"),
        state=location_data.get("state"),
        lga=location_data.get("lga"),
        area=location_data.get("area"),
        market=location_data.get("market"),
    )

    if location:
        return location[0]

    return await locations_db.create_location(
        country=location_data["country"],
        state=location_data.get("state"),
        lga=location_data.get("lga"),
        area=location_data.get("area"),
        market=location_data.get("market"),
    )


async def _resolve_source(source_id, source_name):
    if source_id:
        return await sources_db.get_source_by_id(source_id)

    if not source_name:
        return None

    source_type = "USER"

    return await sources_db.get_source_by_name_and_type(
        name=source_name,
        source_type=source_type,
    )

async def _resolve_product(
    product_name: str,
    brand: Optional[str],
    creator_id: Optional[str],
):
    products = await products_db.find_products(
        name=product_name,
        limit=20,
    )

    for product in products:
        if (
            product.get("name", "").strip().lower()
            == product_name.strip().lower()
        ):
            return product

    if not creator_id:
        raise InvalidRawObservationError(
            "Product does not exist and creator ID "
            "was not provided."
        )

    return await products_db.create_product(
        creator_id=creator_id,
        name=product_name,
        brand=brand,
    )


async def _resolve_variant(
    product_id: str,
    variant_name: str,
    attributes: dict,
):
    variant = await product_variants_db.find_variant(
        product_id=product_id,
        name=variant_name,
    )

    if variant:
        return variant

    return await product_variants_db.create_product_variant(
        product_id=product_id,
        name=variant_name,
        attributes=attributes,
    )


async def _create_price_observation(
    *,
    mapped: dict,
    product: dict,
    variant: dict,
    location: dict,
    source: Optional[dict],
    submitted_by: Optional[str],
):
    return await create_price_observation(
        product_id=str(product["_id"]),
        variant_id=str(variant["_id"]),
        price=mapped["price"],
        location_id=str(location["_id"]),
        observed_at=mapped["observed_at"],
        submitted_by=submitted_by,
        seller_type=mapped["seller_type"],
        source_id=str(source["_id"]) if source else None,
        evidence={"type": "RAW_OBSERVATION"},
    )


async def get_raw_observation(
    observation_id: str,
):
    if not isinstance(observation_id, str):
        raise InvalidRawObservationError(
            "Raw observation ID must be a string."
        )

    observation_id = observation_id.strip()

    if not observation_id:
        raise InvalidRawObservationError(
            "Raw observation ID cannot be empty."
        )

    observation = (
        await raw_observations_db
        .get_raw_observation_by_id(
            observation_id
        )
    )

    if observation is None:
        raise RawObservationNotFoundError(
            "Raw observation not found."
        )

    return observation


async def create_raw_observation(
    *,
    input_format: str,
    payload: dict,
    source_id: Optional[str] = None,
    processing_status: str = PENDING,
):
    input_format = _normalize_input_format(
        input_format
    )

    if not isinstance(payload, dict):
        raise InvalidRawObservationError(
            "Payload must be an object."
        )

    if not payload:
        raise InvalidRawObservationError(
            "Payload cannot be empty."
        )

    processing_status = _validate_processing_status(
        processing_status
    )

    if source_id is not None:
        if not isinstance(source_id, str):
            raise InvalidRawObservationError(
                "Source ID must be a string."
            )

        source_id = source_id.strip()

        if not source_id:
            source_id = None

    return await raw_observations_db.create_raw_observation(
        input_format=input_format,
        payload=payload,
        source_id=source_id,
        processing_status=processing_status,
    )


async def get_raw_observations_by_status(
    processing_status: str,
):
    processing_status = _validate_processing_status(
        processing_status
    )

    return await (
        raw_observations_db
        .get_raw_observations_by_status(
            processing_status
        )
    )


async def get_raw_observations_by_format(
    input_format: str,
):
    input_format = _normalize_input_format(
        input_format
    )

    return await (
        raw_observations_db
        .get_raw_observations_by_format(
            input_format
        )
    )


async def update_processing_status(
    *,
    observation_id: str,
    processing_status: str,
):
    processing_status = _validate_processing_status(
        processing_status
    )

    observation = await get_raw_observation(
        observation_id
    )

    current_status = observation.get(
        "processing_status"
    )

    if current_status == PROCESSED:
        raise InvalidRawObservationError(
            "A processed raw observation cannot "
            "change status."
        )

    if current_status == REJECTED:
        raise InvalidRawObservationError(
            "A rejected raw observation cannot "
            "change status."
        )

    updated = await (
        raw_observations_db
        .update_processing_status(
            observation_id,
            processing_status,
        )
    )

    if updated is None:
        raise RawObservationNotFoundError(
            "Raw observation not found."
        )

    return updated


async def process_raw_observation(
    observation_id: str,
    creator_id: Optional[str] = None,
    submitted_by: Optional[str] = None,
):
    observation = await get_raw_observation(
        observation_id
    )

    current_status = observation.get(
        "processing_status"
    )

    if current_status == PROCESSED:
        return observation

    if current_status == PROCESSING:
        raise RawObservationProcessingError(
            "Raw observation is already being "
            "processed."
        )

    if current_status in {
        REJECTED,
        FAILED,
    }:
        raise RawObservationProcessingError(
            f"Raw observation cannot be processed "
            f"from status {current_status}."
        )

    input_format = _normalize_input_format(
        observation["input_format"]
    )

    await raw_observations_db.update_processing_status(
        observation_id,
        PROCESSING,
    )

    try:
        mapped = _map_payload(
            input_format,
            observation["payload"],
        )

        product = await _resolve_product(
            product_name=mapped["product_name"],
            brand=mapped["brand"],
            creator_id=creator_id,
        )

        if not product:
            raise RawObservationProcessingFailedError(
                "Unable to resolve product."
            )

        variant = await _resolve_variant(
            product_id=str(product["_id"]),
            variant_name=mapped["variant_name"],
            attributes=mapped[
                "variant_attributes"
            ],
        )

        if not variant:
            raise RawObservationProcessingFailedError(
                "Unable to resolve product variant."
            )

        location = await _resolve_location(
            mapped["location"]
        )

        if not location:
            raise RawObservationProcessingFailedError(
                "Unable to resolve location."
            )

        source = await _resolve_source(
            source_id=(
                str(observation["source_id"])
                if observation.get("source_id")
                else None
            ),
            source_name=mapped["source"],
        )

        price_observation = await _create_price_observation(
            mapped=mapped,
            product=product,
            variant=variant,
            location=location,
            source=source,
            submitted_by=submitted_by,
        )

        if not price_observation:
            raise RawObservationProcessingFailedError(
                "Unable to create price observation."
            )

        processed = await raw_observations_db.update_processing_result(
            observation_id=observation_id,
            price_observation_id=str(price_observation["_id"]),
        )


        if processed is None:
            raise RawObservationProcessingFailedError(
                "Failed to save raw observation processing result."
        )

        return processed

    except Exception:
        await (
            raw_observations_db
            .update_processing_status(
                observation_id,
                FAILED,
            )
        )
        raise


async def process_pending_raw_observations(
    input_format: Optional[str] = None,
    creator_id: Optional[str] = None,
    submitted_by: Optional[str] = None,
):
    if input_format:
        input_format = _normalize_input_format(
            input_format
        )

        observations = await (
            raw_observations_db
            .get_raw_observations_by_format(
                input_format
            )
        )

        observations = [
            observation
            for observation in observations
            if observation.get(
                "processing_status"
            ) == PENDING
        ]

    else:
        observations = await (
            raw_observations_db
            .get_raw_observations_by_status(
                PENDING
            )
        )

    results = []

    for observation in observations:
        observation_id = str(
            observation["_id"]
        )

        try:
            processed = await process_raw_observation(
                observation_id=observation_id,
                creator_id=creator_id,
                submitted_by=submitted_by,
            )

            results.append(
                {
                    "observation_id": observation_id,
                    "status": PROCESSED,
                    "result": processed,
                }
            )

        except Exception as exc:
            results.append(
                {
                    "observation_id": observation_id,
                    "status": FAILED,
                    "error": str(exc),
                }
            )

    return results

async def find_raw_observations(
    *,
    input_format: Optional[str] = None,
    processing_status: Optional[str] = None,
    source_id: Optional[str] = None,
):
    if input_format is not None:
        input_format = _normalize_input_format(
            input_format
        )

    if processing_status is not None:
        processing_status = _validate_processing_status(
            processing_status
        )

    if source_id is not None:
        source_id = _validate_required_string(
            source_id,
            "Source ID",
        )

    return await raw_observations_db.find_raw_observations(
        input_format=input_format,
        processing_status=processing_status,
        source_id=source_id,
)
    

async def queue_process_pending_raw_observations(
    *,
    input_format: Optional[str] = None,
    creator_id: Optional[str] = None,
    submitted_by: Optional[str] = None,
):
    observations = await find_raw_observations(
        input_format=input_format,
        processing_status="PENDING",
    )

    for observation in observations:
        observation_id = str(observation["_id"])

        await task_queue.submit(
            "process_raw_observation",
            process_raw_observation,
            observation_id=observation_id,
            creator_id=creator_id,
            submitted_by=submitted_by,
        )

    return {
        "message": "Pending raw observations queued for processing",
        "queued_count": len(observations),
    }