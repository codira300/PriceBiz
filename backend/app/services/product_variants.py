from typing import Optional

from app.database import product_variants as product_variants_db
from app.database.products import get_product_by_id
from app.services.cache import cache


MAX_VARIANT_NAME_LENGTH = 200
PRODUCT_VARIANT_CACHE_TTL = 300


class ProductVariantServiceError(Exception):
    pass


class InvalidProductVariantError(ProductVariantServiceError):
    pass


class ProductVariantNotFoundError(ProductVariantServiceError):
    pass


class ProductNotFoundForVariantError(ProductVariantServiceError):
    pass


def _validate_required_id(
    value: str,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise InvalidProductVariantError(
            f"{field_name} must be a string"
        )

    value = value.strip()

    if not value:
        raise InvalidProductVariantError(
            f"{field_name} cannot be empty"
        )

    return value


def _validate_variant_name(
    name: str,
) -> str:
    if not isinstance(name, str):
        raise InvalidProductVariantError(
            "Variant name must be a string"
        )

    name = name.strip()

    if not name:
        raise InvalidProductVariantError(
            "Variant name cannot be empty"
        )

    if len(name) > MAX_VARIANT_NAME_LENGTH:
        raise InvalidProductVariantError(
            f"Variant name cannot exceed "
            f"{MAX_VARIANT_NAME_LENGTH} characters"
        )

    return name


def _validate_attributes(
    attributes: Optional[dict],
) -> dict:
    if attributes is None:
        return {}

    if not isinstance(attributes, dict):
        raise InvalidProductVariantError(
            "Variant attributes must be an object"
        )

    return attributes


async def create_product_variant(
    *,
    product_id: str,
    name: str,
    attributes: Optional[dict] = None,
):
    product_id = _validate_required_id(
        product_id,
        "Product ID",
    )

    name = _validate_variant_name(name)

    attributes = _validate_attributes(attributes)

    product = await get_product_by_id(product_id)

    if product is None:
        raise ProductNotFoundForVariantError(
            "Product not found"
        )

    existing_variant = (
        await product_variants_db.find_variant(
            product_id,
            name,
        )
    )

    if existing_variant is not None:
        raise InvalidProductVariantError(
            "A variant with this name already exists "
            "for this product"
        )

    variant = await product_variants_db.create_product_variant(
    product_id=product_id,
    name=name,
    attributes=attributes,
)

    if variant is not None:
        cache.delete(
            f"product_variants:{product_id}"
        )
        cache.delete_prefix(
            f"product:{product_id}"
        )
        cache.delete_prefix("search:")
        cache.delete_prefix("product_search:")
        cache.delete_prefix("price_analysis:")

    return variant


async def get_product_variant(
    variant_id: str,
):
    variant_id = _validate_required_id(
        variant_id,
        "Product variant ID",
    )

    cache_key = f"product_variant:{variant_id}"

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    variant = (
        await product_variants_db.get_variant_by_id(
            variant_id
        )
    )

    if variant is None:
        raise ProductVariantNotFoundError(
            "Product variant not found"
        )

    cache.set(
        cache_key,
        variant,
        PRODUCT_VARIANT_CACHE_TTL,
    )

    return variant


async def get_product_variants(
    product_id: str,
):
    product_id = _validate_required_id(
        product_id,
        "Product ID",
    )

    product = await get_product_by_id(
        product_id
    )

    if product is None:
        raise ProductNotFoundForVariantError(
            "Product not found"
        )

    cache_key = (f"product_variants:{product_id}")

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    variants = (
        await product_variants_db.get_variants_by_product(
            product_id
        )
    )

    cache.set(cache_key, variants, PRODUCT_VARIANT_CACHE_TTL,)

    return variants

async def find_product_variant(
    *,
    product_id: str,
    name: Optional[str] = None,
):
    product_id = _validate_required_id(
        product_id,
        "Product ID",
    )

    product = await get_product_by_id(
        product_id
    )

    if product is None:
        raise ProductNotFoundForVariantError(
            "Product not found"
        )

    if name is not None:
        name = _validate_variant_name(name)

    return await product_variants_db.find_variant(
        product_id,
        name,
    )


async def update_product_variant(
    *,
    variant_id: str,
    name: Optional[str] = None,
    attributes: Optional[dict] = None,
):
    variant_id = _validate_required_id(
        variant_id,
        "Product variant ID",
    )

    variant = (
        await product_variants_db.get_variant_by_id(
            variant_id
        )
    )

    if variant is None:
        raise ProductVariantNotFoundError(
            "Product variant not found"
        )

    if name is None and attributes is None:
        raise InvalidProductVariantError(
            "At least one field must be provided"
            " for update"
        )

    updates = {}

    if name is not None:
        name = _validate_variant_name(name)

        existing_variant = (
            await product_variants_db.find_variant(
                str(variant["product_id"]),
                name,
            )
        )

        if (
            existing_variant is not None
            and existing_variant["_id"] != variant["_id"]
        ):
            raise InvalidProductVariantError(
                "A variant with this name already exists "
                "for this product"
            )

        updates["name"] = name

    if attributes is not None:
        attributes = _validate_attributes(
            attributes
        )

        updates["attributes"] = attributes

    updated_variant = (
        await product_variants_db.update_product_variant(
            variant_id,
            updates,
        )
    )

    if updated_variant is None:
        raise ProductVariantNotFoundError(
            "Product variant not found"
        )
    
        cache.delete(
        f"product_variant:{variant_id}"
    )
    cache.delete(
        f"product_variants:{variant['product_id']}"
    )
    cache.delete_prefix(
        f"product:{variant['product_id']}"
    )
    cache.delete_prefix("search:")
    cache.delete_prefix("product_search:")
    cache.delete_prefix("price_analysis:")

    return updated_variant