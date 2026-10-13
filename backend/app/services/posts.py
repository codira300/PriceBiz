from datetime import datetime, timezone, timedelta
from typing import Optional

from bson import ObjectId

from app.database.posts import (
    create_post as db_create_post,
    get_post_by_id,
    get_posts,
    get_feed as db_get_feed,
    get_posts_by_user as db_get_posts_by_user,
    get_posts_by_product as db_get_posts_by_product,
    get_posts_by_location as db_get_posts_by_location,
    update_post as db_update_post,
    delete_post as db_delete_post,
)

from app.database.products import get_product_by_id
from app.database.product_variants import get_variant_by_id
from app.database.locations import get_location_by_id


POST_EDIT_WINDOW_MINUTES = 5

ACTIVE = "ACTIVE"
FLAGGED = "FLAGGED"
REJECTED = "REJECTED"

VALID_POST_TYPES = {
    "GENERAL",
    "PRODUCT_CREATION",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_object_id(value: str, resource: str) -> ObjectId:
    if not isinstance(value, str) or not ObjectId.is_valid(value):
        raise ValueError(f"Invalid {resource} ID")

    return ObjectId(value)


def _validate_post_type(post_type: str) -> str:
    if not isinstance(post_type, str):
        raise ValueError("Post type must be a string")

    post_type = post_type.strip().upper()

    if post_type not in VALID_POST_TYPES:
        raise ValueError("Invalid post type")

    return post_type


async def create_post(
    author_id: str,
    content: str,
    post_type: str = "GENERAL",
    product_id: Optional[str] = None,
    variant_id: Optional[str] = None,
    location_id: Optional[str] = None,
):
    """
    Create a community post.

    A post may optionally be associated with:
    - a product
    - a product variant
    - a location

    PRODUCT_CREATION posts must have a product_id.
    """


    if not content or not content.strip():
        raise ValueError("Post content cannot be empty")


    post_type = _validate_post_type(post_type)


    author_object_id = _validate_object_id(author_id, "author")

    product_object_id = None

    if product_id:
        product_object_id = _validate_object_id(
            product_id,
            "product",
        )

        product = await get_product_by_id(product_id)

        if not product:
            raise ValueError("Product not found")


    variant_object_id = None

    if variant_id:

        if not product_object_id:
            raise ValueError(
                "A variant cannot be attached without a product"
            )

        variant_object_id = _validate_object_id(
            variant_id,
            "variant",
        )

        variant = await get_variant_by_id(variant_id)

        if not variant:
            raise ValueError("Variant not found")

        if variant.get("product_id") != product_object_id:
            raise ValueError(
                "Variant does not belong to the specified product"
            )


    location_object_id = None

    if location_id:

        location_object_id = _validate_object_id(
            location_id,
            "location",
        )

        location = await get_location_by_id(location_id)

        if not location:
            raise ValueError("Location not found")


    if post_type == "PRODUCT_CREATION" and not product_object_id:
        raise ValueError(
            "PRODUCT_CREATION posts must have a product"
        )

    now = _now()

    post = {
        "author_id": author_object_id,
        "content": content.strip(),
        "post_type": post_type,
        "product_id": product_object_id,
        "variant_id": variant_object_id,
        "location_id": location_object_id,
        "status": ACTIVE,
        "created_at": now,
        "updated_at": now,
        "stats": {
            "comments_count": 0,
            "upvotes": 0,
            "downvotes": 0,
        },
    }

    return await db_create_post(post)


async def create_product_creation_post(
    creator_id: str,
    product_id: str,
    content: Optional[str] = None,
    variant_id: Optional[str] = None,
    location_id: Optional[str] = None,
):
    """
    Create the community post automatically associated
    with a newly created product.
    """

    _validate_object_id(product_id, "product")

    product = await get_product_by_id(product_id)

    if not product:
        raise ValueError("Product not found")

    if content is None:
        content = (
            f"New product added: "
            f"{product.get('name', 'Unknown product')}"
        )

    return await create_post(
        author_id=creator_id,
        content=content,
        post_type="PRODUCT_CREATION",
        product_id=product_id,
        variant_id=variant_id,
        location_id=location_id,
    )


async def get_post(post_id: str):
    post_object_id = _validate_object_id(post_id, "post")

    return await get_post_by_id(post_object_id)


async def list_posts(
    post_type: Optional[str] = None,
    product_id: Optional[str] = None,
    author_id: Optional[str] = None,
    location_id: Optional[str] = None,
    status: Optional[str] = ACTIVE,
    limit: int = 20,
    skip: int = 0,
):
    """
    Retrieve posts using optional filters.
    """

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")

    if skip < 0:
        raise ValueError("Skip cannot be negative")


    if post_type is not None:
        post_type = _validate_post_type(post_type)


    product_object_id = None

    if product_id:
        product_object_id = _validate_object_id(
            product_id,
            "product",
        )


    author_object_id = None

    if author_id:
        author_object_id = _validate_object_id(
            author_id,
            "author",
        )


    location_object_id = None

    if location_id:
        location_object_id = _validate_object_id(
            location_id,
            "location",
        )

    return await get_posts(
        post_type=post_type,
        product_id=product_object_id,
        author_id=author_object_id,
        location_id=location_object_id,
        status=status,
        limit=limit,
        skip=skip,
    )


async def update_post(
    post_id: str,
    author_id: str,
    content: str,
):
    """
    Update a post's content.

    Only the author can edit the post,
    and editing is allowed only within
    the configured edit window.
    """

    if not content or not content.strip():
        raise ValueError("Post content cannot be empty")

    post_object_id = _validate_object_id(
        post_id,
        "post",
    )

    author_object_id = _validate_object_id(
        author_id,
        "author",
    )

    post = await get_post_by_id(post_object_id)

    if post is None:
        return None


    if post.get("author_id") != author_object_id:
        raise PermissionError(
            "You can only edit your own posts"
        )


    created_at = post.get("created_at")

    if created_at is None:
        raise ValueError(
            "Post creation time is missing"
        )

    now = _now()

    if now - created_at > timedelta(
        minutes=POST_EDIT_WINDOW_MINUTES
    ):
        raise PermissionError(
            "The post can no longer be edited"
        )


    return await db_update_post(
        post_object_id,
        {
            "content": content.strip(),
            "updated_at": now,
        },
    )


async def delete_post(
    post_id: str,
    author_id: str,
):
    """
    Delete a post.

    Only the author can delete the post.
    """

    post_object_id = _validate_object_id(
        post_id,
        "post",
    )

    author_object_id = _validate_object_id(
        author_id,
        "author",
    )

    post = await get_post_by_id(post_object_id)

    if post is None:
        return False

    if post.get("author_id") != author_object_id:
        raise PermissionError(
            "You can only delete your own posts"
        )

    return await db_delete_post(post_object_id)


async def flag_post(post_id: str):
    """
    Flag a post for moderation.
    """

    post_object_id = _validate_object_id(
        post_id,
        "post",
    )

    post = await get_post_by_id(post_object_id)

    if post is None:
        return None

    return await db_update_post(
        post_object_id,
        {
            "status": FLAGGED,
            "updated_at": _now(),
        },
    )


async def restore_post(post_id: str):
    """
    Restore a flagged post to ACTIVE.
    """

    post_object_id = _validate_object_id(
        post_id,
        "post",
    )

    post = await get_post_by_id(post_object_id)

    if post is None:
        return None

    return await db_update_post(
        post_object_id,
        {
            "status": ACTIVE,
            "updated_at": _now(),
        },
    )


async def reject_post(post_id: str):
    """
    Reject a post during moderation.
    """

    post_object_id = _validate_object_id(
        post_id,
        "post",
    )

    post = await get_post_by_id(post_object_id)

    if post is None:
        return None

    return await db_update_post(
        post_object_id,
        {
            "status": REJECTED,
            "updated_at": _now(),
        },
    )
    
    
async def get_feed(
    limit: int = 20,
    skip: int = 0,
):
    """
    Get the active posts for the community feed.
    """

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")

    if skip < 0:
        raise ValueError("Skip cannot be negative")


    return await db_get_feed(
        limit=limit,
        skip=skip,
    )


async def get_posts_by_user(
    user_id: str,
    limit: int = 20,
):
    """
    Get active posts created by a specific user.
    """

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")

    user_object_id = _validate_object_id(
        user_id,
        "user",
    )


    return await db_get_posts_by_user(
        user_id=user_object_id,
        limit=limit,
    )


async def get_posts_by_product(
    product_id: str,
    limit: int = 20,
):
    """
    Get active posts associated with a specific product.
    """

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")

    product_object_id = _validate_object_id(
        product_id,
        "product",
    )


    return await db_get_posts_by_product(
        product_id=product_object_id,
        limit=limit,
    )


async def get_posts_by_location(
    location_id: str,
    limit: int = 20,
):
    """
    Get active posts associated with a specific location.
    """

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")

    location_object_id = _validate_object_id(
        location_id,
        "location",
    )

    return await db_get_posts_by_location(
        location_id=location_object_id,
        limit=limit,
    )