from typing import Optional

from app.services import posts as posts_service


async def create_post(
    *,
    author_id: str,
    content: str,
    post_type: str = "GENERAL",
    product_id: Optional[str] = None,
    variant_id: Optional[str] = None,
    location_id: Optional[str] = None,
):
    return await posts_service.create_post(
        author_id=author_id,
        content=content,
        post_type=post_type,
        product_id=product_id,
        variant_id=variant_id,
        location_id=location_id,
    )


async def create_product_creation_post(
    *,
    creator_id: str,
    product_id: str,
    content: Optional[str] = None,
    variant_id: Optional[str] = None,
    location_id: Optional[str] = None,
):
    return await posts_service.create_product_creation_post(
        creator_id=creator_id,
        product_id=product_id,
        content=content,
        variant_id=variant_id,
        location_id=location_id,
    )


async def get_post(
    *,
    post_id: str,
):
    return await posts_service.get_post(
        post_id=post_id,
    )


async def list_posts(
    *,
    post_type: Optional[str] = None,
    product_id: Optional[str] = None,
    author_id: Optional[str] = None,
    location_id: Optional[str] = None,
    status: Optional[str] = "ACTIVE",
    limit: int = 20,
    skip: int = 0,
):
    return await posts_service.list_posts(
        post_type=post_type,
        product_id=product_id,
        author_id=author_id,
        location_id=location_id,
        status=status,
        limit=limit,
        skip=skip,
    )


async def get_feed(
    *,
    limit: int = 20,
    skip: int = 0,
):
    return await posts_service.get_feed(
        limit=limit,
        skip=skip,
    )


async def get_posts_by_user(
    *,
    user_id: str,
    limit: int = 20,
):
    return await posts_service.get_posts_by_user(
        user_id=user_id,
        limit=limit,
    )


async def get_posts_by_product(
    *,
    product_id: str,
    limit: int = 20,
):
    return await posts_service.get_posts_by_product(
        product_id=product_id,
        limit=limit,
    )


async def get_posts_by_location(
    *,
    location_id: str,
    limit: int = 20,
):
    return await posts_service.get_posts_by_location(
        location_id=location_id,
        limit=limit,
    )


async def update_post(
    *,
    post_id: str,
    author_id: str,
    content: str,
):
    return await posts_service.update_post(
        post_id=post_id,
        author_id=author_id,
        content=content,
    )


async def delete_post(
    *,
    post_id: str,
    author_id: str,
):
    return await posts_service.delete_post(
        post_id=post_id,
        author_id=author_id,
    )


async def flag_post(
    *,
    post_id: str,
):
    return await posts_service.flag_post(
        post_id=post_id,
    )


async def restore_post(
    *,
    post_id: str,
):
    return await posts_service.restore_post(
        post_id=post_id,
    )


async def reject_post(
    *,
    post_id: str,
):
    return await posts_service.reject_post(
        post_id=post_id,
    )