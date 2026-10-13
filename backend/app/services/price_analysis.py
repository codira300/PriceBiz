from datetime import datetime, timezone
from statistics import quantiles
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId

from app.database.price_observations import (
    find_price_observations,
)
from app.database.products import get_product_by_id
from app.database.product_variants import (
    get_variant_by_id,
    get_variants_by_product,
)
from app.database.locations import get_location_by_id
from app.services.cache import cache


MIN_LOCATION_OBSERVATIONS = 5
IQR_MULTIPLIER = 1.5
PRICE_ANALYSIS_CACHE_TTL = 60


def _validate_object_id(
    value: str,
    resource: str,
) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise ValueError(
            f"Invalid {resource} ID"
        )


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_location_value(
    value,
) -> Optional[str]:
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value.casefold()


def _get_price_amount(
    observation: dict,
) -> Optional[int]:
    price = observation.get("price")

    if isinstance(price, dict):
        amount = price.get("amount")
    else:
        amount = price

    if amount is None:
        return None

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return None

    if amount <= 0:
        return None

    return amount


def _calculate_iqr_bounds(
    prices: list[int],
):
    if len(prices) < 4:
        return None, None

    values = sorted(prices)

    quartiles = quantiles(
        values,
        n=4,
        method="inclusive",
    )

    q1 = quartiles[0]
    q3 = quartiles[2]

    iqr = q3 - q1

    lower_bound = q1 - (
        IQR_MULTIPLIER * iqr
    )

    upper_bound = q3 + (
        IQR_MULTIPLIER * iqr
    )

    return lower_bound, upper_bound


def _separate_outliers(
    observations: list[dict],
):
    if not observations:
        return [], []

    valid_observations = [
        observation
        for observation in observations
        if _get_price_amount(observation)
        is not None
    ]

    if not valid_observations:
        return [], []

    prices = [
        _get_price_amount(observation)
        for observation in valid_observations
    ]

    lower_bound, upper_bound = (
        _calculate_iqr_bounds(prices)
    )

    if (
        lower_bound is None
        or upper_bound is None
    ):
        return valid_observations, []

    normal = []
    outliers = []

    for observation in valid_observations:
        amount = _get_price_amount(
            observation
        )

        if (
            amount < lower_bound
            or amount > upper_bound
        ):
            outliers.append(observation)
        else:
            normal.append(observation)


    if not normal:
        return valid_observations, []

    return normal, outliers


def _location_matches(
    observation: dict,
    location: dict,
):
    observation_location = observation.get(
        "location"
    )

    if not observation_location:
        return False

    for field in (
        "country",
        "state",
        "lga",
        "area",
        "market",
    ):
        requested_value = (
            _normalize_location_value(
                location.get(field)
            )
        )

        if requested_value is None:
            continue

        observation_value = (
            _normalize_location_value(
                observation_location.get(
                    field
                )
            )
        )

        if observation_value != requested_value:
            return False

    return True


def _broaden_location(
    location: dict,
):
    broader = dict(location)

    if broader.get("market"):
        broader["market"] = None
        return broader

    if broader.get("area"):
        broader["area"] = None
        return broader

    if broader.get("lga"):
        broader["lga"] = None
        return broader

    if broader.get("state"):
        broader["state"] = None
        return broader

    if broader.get("country"):
        broader["country"] = None
        return broader

    return None


def _get_observations_for_location(
    observations: list[dict],
    location: dict,
):
    return [
        observation
        for observation in observations
        if _location_matches(
            observation,
            location,
        )
    ]


def _select_location_data(
    observations: list[dict],
    location: Optional[dict],
):
    if not location:
        return observations, None

    current_location = dict(location)

    while current_location:
        matching = (
            _get_observations_for_location(
                observations,
                current_location,
            )
        )

        if len(matching) >= (
            MIN_LOCATION_OBSERVATIONS
        ):
            return (
                matching,
                current_location,
            )

        current_location = _broaden_location(
            current_location
        )

    return [], None


def _seller_type_analysis(
    observations: list[dict],
):
    seller_groups = {}

    for observation in observations:
        seller_type = observation.get(
            "seller_type"
        )

        if not seller_type:
            continue

        seller_type = str(
            seller_type
        ).strip().upper()

        if not seller_type:
            continue

        seller_groups.setdefault(
            seller_type,
            [],
        ).append(observation)

    result = {}

    for (
        seller_type,
        seller_observations,
    ) in seller_groups.items():

        normal, outliers = (
            _separate_outliers(
                seller_observations
            )
        )

        if not normal:
            continue

        prices = [
            _get_price_amount(observation)
            for observation in normal
        ]

        prices = [
            price
            for price in prices
            if price is not None
        ]

        if not prices:
            continue

        result[seller_type] = {
            "minimum": min(prices),
            "maximum": max(prices),
            "observation_count": len(
                seller_observations
            ),
            "normal_observation_count": len(
                normal
            ),
            "outlier_count": len(
                outliers
            ),
            "other_observations": [
                _serialize_observation(
                    observation
                )
                for observation in outliers
            ],
        }

    return result


def _build_trend(
    observations: list[dict],
):
    trend = []

    for observation in observations:
        observed_at = observation.get(
            "observed_at"
        )

        if isinstance(
            observed_at,
            datetime,
        ):
            observed_at = (
                observed_at.isoformat()
            )

        price = _get_price_amount(
            observation
        )

        if price is None:
            continue

        trend.append(
            {
                "date": observed_at,
                "price": price,
                "seller_type": observation.get(
                    "seller_type"
                ),
            }
        )

    trend.sort(
        key=lambda item: (
            item["date"] or ""
        )
    )

    return trend


def _serialize_location(
    location: Optional[dict],
):
    if not location:
        return None

    result = dict(location)

    if "_id" in result:
        result["_id"] = str(
            result["_id"]
        )

    return result


def _serialize_observation(
    observation: dict,
):
    result = dict(observation)

    if "_id" in result:
        result["_id"] = str(
            result["_id"]
        )

    for field in (
        "product_id",
        "variant_id",
        "location_id",
        "source_id",
        "submitted_by",
    ):
        if (
            field in result
            and result[field]
        ):
            result[field] = str(
                result[field]
            )

    if isinstance(
        result.get("observed_at"),
        datetime,
    ):
        result["observed_at"] = (
            result[
                "observed_at"
            ].isoformat()
        )

    return result


async def _attach_locations(
    observations: list[dict],
):
    """
    Resolve location_id for each observation
    and attach the location document.

    The database stores location_id on price
    observations, while the analysis layer
    needs the actual location fields.
    """

    location_cache = {}

    enriched = []

    for observation in observations:
        observation_copy = dict(
            observation
        )

        location_id = observation.get(
            "location_id"
        )

        if location_id:
            location_key = str(
                location_id
            )

            if (
                location_key
                not in location_cache
            ):
                location = (
                    await get_location_by_id(
                        location_key
                    )
                )

                location_cache[
                    location_key
                ] = location
            else:
                location = (
                    location_cache[
                        location_key
                    ]
                )

            observation_copy[
                "location"
            ] = location

        enriched.append(
            observation_copy
        )

    return enriched


def _build_no_data_response(
    product_id: str,
    variant_id: Optional[str],
):
    return {
        "type": "NO_DATA",
        "product_id": product_id,
        "variant_id": variant_id,
        "location": None,
        "price_summary": {
            "type": "NO_DATA",
            "minimum": None,
            "maximum": None,
            "currency": "NGN",
            "observation_count": 0,
            "normal_observation_count": 0,
            "outlier_count": 0,
            "other_observations": [],
        },
        "seller_types": {},
        "trend": [],
        "observations": [],
    }


async def analyze_variant_prices(
    product_id: str,
    variant_id: Optional[str] = None,
    location_id: Optional[str] = None,
):
    """
    Analyze active price observations.

    Location strategy:

    1. Use the requested location when
       sufficient observations exist.
    2. If fewer than five exist, broaden:
       market -> area -> LGA -> state -> country.
    3. If no requested location was supplied,
       use all observations.

    Price strategy:

    1. Ignore invalid price observations.
    2. Use IQR for outlier detection when
       at least four observations exist.
    3. Calculate the normal price range from
       non-outlier observations.
    4. Analyze seller types independently.
    5. Return historical observations for
       trend/charting.
    """


    product = await get_product_by_id(
        product_id
    )

    if not product:
        return None


    if variant_id:
        _validate_object_id(
            variant_id,
            "variant",
        )

        variant = await get_variant_by_id(
            variant_id
        )

        if not variant:
            return None

        if str(
            variant["product_id"]
        ) != str(product_id):
            return None

    location = None

    if location_id:
        _validate_object_id(
            location_id,
            "location",
        )

        location = (
            await get_location_by_id(
                location_id
            )
        )

        if not location:
            return None
        
    cache_key = (
        f"price_analysis:variant:"
        f"{product_id}:"
        f"{variant_id or 'all'}:"
        f"{location_id or 'all'}"
    )

    cached = cache.get(cache_key)

    if cached is not None:
        return cached    
    
    observations = await find_price_observations(
        product_id=product_id,
        variant_id=variant_id,
        status="ACTIVE",
        limit=1000,
    )

    if not observations:
        result = _build_no_data_response(
            product_id,
            variant_id,
        )

        cache.set(
            cache_key,
            result,
            PRICE_ANALYSIS_CACHE_TTL,
        )

        return result

    observations = (
        await _attach_locations(
            observations
        )
    )

    observations = [
        observation
        for observation in observations
        if (
            _get_price_amount(
                observation
            )
            is not None
            and observation.get(
                "observed_at"
            ) is not None
        )
    ]

    if not observations:
        result = _build_no_data_response(
            product_id,
            variant_id,
        )

        cache.set(
            cache_key,
            result,
            PRICE_ANALYSIS_CACHE_TTL,
        )

        return result
        

    observations.sort(
        key=lambda item: item.get(
            "observed_at"
        ),
        reverse=True,
    )


    (
        selected_observations,
        selected_location,
    ) = _select_location_data(
        observations,
        location,
    )


    if (
        location
        and not selected_observations
    ):
        result = _build_no_data_response(
            product_id,
            variant_id,
        )

        cache.set(
            cache_key,
            result,
            PRICE_ANALYSIS_CACHE_TTL,
        )

        return result


    if not selected_observations:
        selected_observations = observations

    if not selected_observations:
        result = _build_no_data_response(
            product_id,
            variant_id,
        )

        cache.set(
            cache_key,
            result,
            PRICE_ANALYSIS_CACHE_TTL,
        )

        return result

    normal, outliers = (
        _separate_outliers(
            selected_observations
        )
    )

    if not normal:
        result = _build_no_data_response(
            product_id,
            variant_id,
        )

        cache.set(
            cache_key,
            result,
            PRICE_ANALYSIS_CACHE_TTL,
        )

        return result

    prices = [
        _get_price_amount(observation)
        for observation in normal
    ]

    prices = [
        price
        for price in prices
        if price is not None
    ]

    if not prices:
        result = _build_no_data_response(
            product_id,
            variant_id,
        )

        cache.set(
            cache_key,
            result,
            PRICE_ANALYSIS_CACHE_TTL,
        )

        return result

    summary = {
        "type": "PRICE_RANGE",
        "minimum": min(prices),
        "maximum": max(prices),
        "currency": "NGN",
        "observation_count": len(
            selected_observations
        ),
        "normal_observation_count": len(
            normal
        ),
        "outlier_count": len(
            outliers
        ),
        "other_observations": [
            _serialize_observation(
                observation
            )
            for observation in outliers
        ],
    }


    result = {
        "type": "PRICE_ANALYSIS",
        "product_id": product_id,
        "variant_id": variant_id,
        "location": _serialize_location(
            selected_location
        ),
        "price_summary": summary,
        "seller_types": _seller_type_analysis(
            selected_observations
        ),
        "trend": _build_trend(
            selected_observations
        ),
        "observations": [
            _serialize_observation(
                observation
            )
            for observation in selected_observations
        ],
    }

    cache.set(
        cache_key,
        result,
        PRICE_ANALYSIS_CACHE_TTL,
    )

    return result


async def analyze_product_prices(
    product_id: str,
    location_id: Optional[str] = None,
):
    """
    Analyze every variant belonging to a
    product.
    """

    cache_key = (
        f"price_analysis:product:"
        f"{product_id}:"
        f"{location_id or 'all'}"
    )

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    product = await get_product_by_id(
        product_id
    )

    if not product:
        return None

    variants = (
        await get_variants_by_product(
            product_id
        )
    )

    results = []

    for variant in variants:
        result = (
            await analyze_variant_prices(
                product_id=product_id,
                variant_id=str(
                    variant["_id"]
                ),
                location_id=location_id,
            )
        )

        results.append(
            {
                "variant": {
                    "_id": str(
                        variant["_id"]
                    ),
                    "name": variant.get(
                        "name"
                    ),
                    "attributes": variant.get(
                        "attributes",
                        {},
                    ),
                },
                "analysis": result,
            }
        )

    result = {
        "product": {
            "_id": str(
                product["_id"]
            ),
            "name": product.get(
                "name"
            ),
            "brand": product.get(
                "brand"
            ),
            "category": product.get(
                "category"
            ),
        },
        "variants": results,
    }

    cache.set(
        cache_key,
        result,
        PRICE_ANALYSIS_CACHE_TTL,
    )

    return result