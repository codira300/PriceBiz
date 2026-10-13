from typing import Any, Optional

from app.services import products as products_service


def serialize_product(product: dict):
    return {
        "_id": str(product["_id"]),
        "name": product.get("name"),
        "brand": product.get("brand"),
        "category": product.get("category"),
        "description": product.get("description"),
        "details": product.get("details", {}),
        "packaging": product.get("packaging", {}),
        "creator_id": str(product["creator_id"])
        if product.get("creator_id")
        else None,
        "created_at": product.get("created_at"),
        "updated_at": product.get("updated_at"),
    }


def serialize_variant(variant: Optional[dict]):
    if variant is None:
        return None

    return {
        "_id": str(variant["_id"]),
        "product_id": str(variant["product_id"]),
        "name": variant.get("name"),
        "attributes": variant.get("attributes", {}),
    }


def serialize_post(post: Optional[dict]):
    if post is None:
        return None

    serialized = dict(post)

    if "_id" in serialized:
        serialized["_id"] = str(serialized["_id"])

    if serialized.get("author_id"):
        serialized["author_id"] = str(
            serialized["author_id"]
        )

    if serialized.get("product_id"):
        serialized["product_id"] = str(
            serialized["product_id"]
        )

    return serialized


async def create_product(
    *,
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
    result = await products_service.create_product(
        creator_id=creator_id,
        name=name,
        brand=brand,
        category=category,
        description=description,
        details=details,
        packaging=packaging,
        variant_name=variant_name,
        variant_attributes=variant_attributes,
    )

    if result is None:
        return None

    return {
        "product": serialize_product(
            result["product"]
        ),
        "variant": serialize_variant(
            result.get("variant")
        ),
        "post": serialize_post(
            result.get("post")
        ),
    }


async def get_product(
    *,
    product_id: str,
    include_variants: bool = True,
):
    result = await products_service.get_product(
        product_id=product_id,
        include_variants=include_variants,
    )

    if result is None:
        return None

    response = {
        "product": serialize_product(
            result["product"]
        ),
    }

    if include_variants:
        response["variants"] = [
            serialize_variant(variant)
            for variant in result.get("variants", [])
        ]

    return response


async def search_products(
    *,
    query: str,
    limit: int = 10,
    skip: int = 0,
):
    products = await products_service.search_products(
        query=query,
        limit=limit,
        skip=skip,
    )

    return [
        serialize_product(product)
        for product in products
    ]


async def update_product(
    *,
    product_id: str,
    user_id: str,
    updates: dict,
):
    product = await products_service.update_product(
        product_id=product_id,
        user_id=user_id,
        updates=updates,
    )

    if product is None:
        return None

    return serialize_product(product)


async def delete_product(
    *,
    product_id: str,
    user_id: str,
):
    return await products_service.delete_product(
        product_id=product_id,
        user_id=user_id,
    )
    
    
async def list_products(
    *,
    limit: int = 10,
    skip: int = 0,
):
    products = await products_service.list_products(
        limit=limit,
        skip=skip,
    )

    return [
        serialize_product(product)
        for product in products
    ]