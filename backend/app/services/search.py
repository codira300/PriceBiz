from app.database import database
from app.services.cache import cache
from bson import ObjectId

SEARCH_CACHE_TTL = 30

def calculate_product_relevance(
    product: dict,
    search_term: str,
) -> int:
    search_term = search_term.lower()

    name = product.get("name", "").lower()
    brand = product.get("brand", "").lower()
    category = product.get("category", "").lower()

    if name == search_term:
        return 1

    if name.startswith(search_term):
        return 2

    if search_term in name:
        return 3

    if search_term in brand:
        return 4

    if search_term in category:
        return 5

    return 6


def variant_matches_search(
    variant: dict,
    search_term: str,
) -> bool:
    search_term = search_term.lower()

    name = variant.get("name", "").lower()

    if search_term in name:
        return True

    attributes = variant.get("attributes") or {}

    for value in attributes.values():
        if search_term in str(value).lower():
            return True

    return False


async def search_products(
    search_term: str,
    limit: int = 20,
):
    search_term = search_term.strip()

    cache_key = (
        f"search:{search_term.lower()}:{limit}"
    )

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    if not search_term:
        return []

    search_regex = {
        "$regex": search_term,
        "$options": "i",
    }

    product_matches = await database.products.find(
        {
            "$or": [
                {"name": search_regex},
                {"brand": search_regex},
                {"category": search_regex},
            ]
        }
    ).to_list(length=limit)

    variant_matches = await database.product_variants.find(
        {
            "$or": [
                {"name": search_regex},
                {"attributes": search_regex},
            ]
        }
    ).to_list(length=limit)

    # Collect product IDs as strings, from both products and variants.
    product_ids = {
        str(product["_id"])
        for product in product_matches
    }

    product_ids.update(
        str(variant["product_id"])
        for variant in variant_matches
    )

    if not product_ids:
        return []

    object_product_ids = [
        ObjectId(product_id)
        for product_id in product_ids
        if ObjectId.is_valid(product_id)
    ]

    products = await database.products.find(
        {
            "_id": {
                "$in": object_product_ids
            }
        }
    ).to_list(length=None)

    product_lookup = {
        str(product["_id"]): product
        for product in products
    }

    # product_id in product_variants is stored as a string
    # (that's why the aggregation below matches on strings).
    variants = await database.product_variants.find(
        {
            "product_id": {
                "$in": list(product_ids)
            }
        }
    ).to_list(length=None)

    # NOTE: `aggregate()` is NOT awaitable in Motor.
    # It returns an AsyncIOMotorLatentCommandCursor; iterate
    # it with `async for` or call `.to_list()` on it.
    observation_cursor = database.price_observations.aggregate(
        [
            {
                "$match": {
                    "product_id": {
                        "$in": list(product_ids)
                    },
                    "status": "ACTIVE",
                }
            },
            {
                "$group": {
                    "_id": {
                        "product_id": "$product_id",
                        "variant_id": "$variant_id",
                    },
                    "count": {
                        "$sum": 1
                    },
                }
            },
        ]
    )

    observation_counts = await observation_cursor.to_list(
        length=None
    )

    observation_count_lookup = {
        (
            str(item["_id"]["product_id"]),
            str(item["_id"]["variant_id"]),
        ): item["count"]
        for item in observation_counts
    }

    variant_match_product_ids = {
        variant["product_id"]
        for variant in variant_matches
    }

    results = []

    for product_id in product_ids:

        product = product_lookup.get(product_id)

        if not product:
            continue

        product_relevance = calculate_product_relevance(
            product,
            search_term,
        )

        product_variants = [
            variant
            for variant in variants
            if str(variant["product_id"]) == product_id
        ]

        for variant in product_variants:

            variant_id = str(variant["_id"])

            observation_count = observation_count_lookup.get(
                (product_id, variant_id),
                0,
            )

            variant_match = (
                product_id in variant_match_product_ids
                and variant_matches_search(
                    variant,
                    search_term,
                )
            )

            if variant_match:
                relevance = min(product_relevance, 4)
            else:
                relevance = product_relevance

            results.append(
                {
                    "relevance": relevance,
                    "product": {
                        "_id": str(product_id),
                        "name": product["name"],
                        "brand": product.get("brand"),
                        "category": product.get("category"),
                    },
                    "variant": {
                        "_id": str(variant_id),
                        "name": variant["name"],
                        "attributes": variant.get("attributes"),
                    },
                    "observation_count": observation_count,
                }
            )

    results.sort(
        key=lambda result: (
            result["relevance"],
            -result["observation_count"],
            result["product"]["name"].lower(),
            result["variant"]["name"].lower(),
        )
    )

    for result in results:
        result.pop("relevance")

    final_results = results[:limit]

    cache.set(
        cache_key,
        final_results,
        SEARCH_CACHE_TTL,
    )

    return final_results