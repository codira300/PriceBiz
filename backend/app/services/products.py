from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from app.database.posts import create_post
from app.database.products import (
    create_product as db_create_product,
    delete_product as db_delete_product,
    find_products as db_find_products,
    get_product_by_id as db_get_product_by_id,
    update_product as db_update_product,
)
from app.database.product_variants import (
    create_product_variant,
    get_variants_by_product,
)
from app.utils import get_object_id
from app.services.cache import cache

PRODUCT_CACHE_TTL = 300
PRODUCT_LIST_CACHE_TTL = 60
PRODUCT_SEARCH_CACHE_TTL = 30

PRODUCT_UPDATE_WINDOW = timedelta(minutes=5)


async def create_product(
    creator_id: str,
    name: str,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    packaging: Optional[dict[str, Any]] = None,
    variant_name: Optional[str] = None,
    variant_attributes: Optional[dict[str, Any]] = None,
):
    product = await db_create_product(
        creator_id=creator_id,
        name=name,
        brand=brand,
        category=category,
        description=description,
        details=details,
        packaging=packaging,
    )

    if product is None:
        return None

    try:
        post = await create_post(
            author_id=creator_id,
            content=f"New product added: {product['name']}",
            post_type="PRODUCT_CREATION",
            product_id=str(product["_id"]),
        )

    except Exception:
        await db_delete_product(
            str(product["_id"])
        )
        raise

    if variant_name:
        variant = await create_product_variant(
            product_id=str(product["_id"]),
            name=variant_name,
            attributes=variant_attributes,
        )
    else:
        variant = None
        
    cache.delete_prefix("products:list:")
    cache.delete_prefix("product_search:")
    cache.delete_prefix("search:")
    
    return {
        "product": product,
        "variant": variant,
        "post": post,
    }


async def get_product(
    product_id: str,
    include_variants: bool = True,
):
    cache_suffix = "with_variants" if include_variants else "without_variants"

    cache_key = (
        f"product:{product_id}:{cache_suffix}"
    )

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    product = await db_get_product_by_id(
        product_id
    )

    if product is None:
        return None

    result = {
        "product": product,
    }

    if include_variants:
        result["variants"] = (
            await get_variants_by_product(
                product_id
            )
        )

    cache.set(
        cache_key,
        result,
        PRODUCT_CACHE_TTL,
    )

    return result


async def search_products(
    query: str,
    limit: int = 10,
    skip: int = 0,
):
    if not query or not query.strip():
        return []

    query = query.strip()

    cache_key = (
        f"product_search:{query.lower()}:"
        f"{limit}:{skip}"
    )

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    products = await db_find_products(
        name=query,
        limit=limit,
        skip=skip,
    )

    cache.set(
        cache_key,
        products,
        PRODUCT_SEARCH_CACHE_TTL,
    )

    return products


async def update_product(
    product_id: str,
    user_id: str,
    updates: dict,
):
    product = await db_get_product_by_id(
        product_id
    )

    if product is None:
        return None

    user_object_id = get_object_id(
        user_id,
        "user",
    )

    if product["creator_id"] != user_object_id:
        raise PermissionError(
            "Only the product creator can update it"
        )

    created_at = product["created_at"]

    if (
        datetime.now(timezone.utc) - created_at
        > PRODUCT_UPDATE_WINDOW
    ):
        raise PermissionError(
            "Product can only be updated "
            "within 5 minutes of creation"
        )

    updated_product = await db_update_product(product_id, updates,)

    if updated_product is not None:
        cache.delete_prefix(
            f"product:{product_id}"
        )
        cache.delete_prefix("products:list:")
        cache.delete_prefix("product_search:")
        cache.delete_prefix("search:")
        cache.delete_prefix("price_analysis:")

    return updated_product


async def delete_product(
    product_id: str,
    user_id: str,
):
    product = await db_get_product_by_id(
        product_id
    )

    if product is None:
        return False

    user_object_id = get_object_id(
        user_id,
        "user",
    )

    if product["creator_id"] != user_object_id:
        raise PermissionError(
            "Only the product creator can delete it"
        )

    deleted = await db_delete_product(product_id)

    if deleted:
        cache.delete_prefix(
            f"product:{product_id}"
        )
        cache.delete_prefix("products:list:")
        cache.delete_prefix("product_search:")
        cache.delete_prefix("search:")
        cache.delete_prefix("price_analysis:")

    return deleted
    

async def list_products(
    *,
    limit: int = 10,
    skip: int = 0,
):
    cache_key = (
        f"products:list:{limit}:{skip}"
    )

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    products = await db_find_products(
        limit=limit,
        skip=skip,
    )

    cache.set(
        cache_key,
        products,
        PRODUCT_LIST_CACHE_TTL,
    )

    return products