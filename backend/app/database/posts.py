from typing import Optional

from bson import ObjectId

from app.database.connection import database


posts_collection = database.posts


async def create_post(post: dict):
    """
    Insert a fully prepared post document.

    Business validation is handled by the service layer.
    """

    author_id = post.get("author_id")

    if not isinstance(author_id, ObjectId):
        raise ValueError("author_id must be an ObjectId")

    author = await database.users.find_one(
        {"_id": author_id}
    )

    if author is None:
        return None

    result = await posts_collection.insert_one(post)

    return await posts_collection.find_one(
        {"_id": result.inserted_id}
    )


async def get_post_by_id(post_id: ObjectId):
    return await posts_collection.find_one(
        {"_id": post_id}
    )


async def get_posts(
    post_type: Optional[str] = None,
    product_id: Optional[ObjectId] = None,
    author_id: Optional[ObjectId] = None,
    location_id: Optional[ObjectId] = None,
    status: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
):
    query = {}

    if post_type:
        query["post_type"] = post_type

    if product_id is not None:
        query["product_id"] = product_id

    if author_id is not None:
        query["author_id"] = author_id

    if location_id is not None:
        query["location_id"] = location_id

    if status:
        query["status"] = status

    cursor = (
        posts_collection
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def update_post(
    post_id: ObjectId,
    updates: dict,
):
    allowed_fields = {
        "content",
        "post_type",
        "product_id",
        "variant_id",
        "location_id",
        "status",
        "updated_at",
    }

    updates = {
        key: value
        for key, value in updates.items()
        if key in allowed_fields
    }

    if not updates:
        return await get_post_by_id(post_id)

    result = await posts_collection.update_one(
        {"_id": post_id},
        {"$set": updates},
    )

    if result.matched_count == 0:
        return None

    return await get_post_by_id(post_id)


async def delete_post(post_id: ObjectId):
    result = await posts_collection.delete_one(
        {"_id": post_id}
    )

    return result.deleted_count > 0


async def get_feed(
    limit: int = 20,
    skip: int = 0,
):
    cursor = (
        posts_collection
        .find({"status": "ACTIVE"})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def get_posts_by_user(
    user_id: ObjectId,
    limit: int = 20,
):
    cursor = (
        posts_collection
        .find({
            "author_id": user_id,
            "status": "ACTIVE",
        })
        .sort("created_at", -1)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def get_posts_by_product(
    product_id: ObjectId,
    limit: int = 20,
):
    cursor = (
        posts_collection
        .find({
            "product_id": product_id,
            "status": "ACTIVE",
        })
        .sort("created_at", -1)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)


async def get_posts_by_location(
    location_id: ObjectId,
    limit: int = 20,
):
    cursor = (
        posts_collection
        .find({
            "location_id": location_id,
            "status": "ACTIVE",
        })
        .sort("created_at", -1)
        .limit(limit)
    )

    return await cursor.to_list(length=limit)