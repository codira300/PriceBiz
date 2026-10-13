from datetime import datetime, timezone
from typing import Optional
from app.database.validation import CommentData
from app.database.connection import database
from app.utils import get_object_id


comments_collection = database.comments

async def create_comment(
    post_id: str,
    author_id: str,
    content: str,
    parent_comment_id: Optional[str] = None,
):
    post_object_id = get_object_id(
        post_id,
        "post",
    )

    author_object_id = get_object_id(
        author_id,
        "user",
    )

    post = await database.posts.find_one(
        {"_id": post_object_id}
    )

    if post is None:
        return None

    author = await database.users.find_one(
        {"_id": author_object_id}
    )

    if author is None:
        return None

    content = content.strip()

    if not content:
        raise ValueError(
            "Comment content cannot be empty"
        )

    parent_object_id = None

    if parent_comment_id:
        parent_object_id = get_object_id(
            parent_comment_id,
            "parent comment",
        )

        parent = await comments_collection.find_one(
            {
                "_id": parent_object_id,
                "post_id": post_object_id,
            }
        )

        if parent is None:
            return None

    now = datetime.now(timezone.utc)

    comment = {
        "post_id": post_object_id,
        "author_id": author_object_id,
        "parent_comment_id": parent_object_id,
        "content": content,
        "created_at": now,
        "updated_at": now,
        "stats": {
            "replies_count": 0,
            "upvotes": 0,
            "downvotes": 0,
        },
    }

    result = await comments_collection.insert_one(
        comment
    )

    await database.posts.update_one(
        {"_id": post_object_id},
        {
            "$inc": {
                "stats.comments_count": 1
            }
        },
    )

    if parent_object_id:
        await comments_collection.update_one(
            {"_id": parent_object_id},
            {
                "$inc": {
                    "stats.replies_count": 1
                }
            },
        )

    return await comments_collection.find_one(
        {"_id": result.inserted_id}
    )


async def get_comment_by_id(
    comment_id: str,
):
    comment_object_id = get_object_id(
        comment_id,
        "comment",
    )

    return await comments_collection.find_one(
        {"_id": comment_object_id}
    )


async def get_post_comments(
    post_id: str,
    limit: int = 50,
):
    post_object_id = get_object_id(
        post_id,
        "post",
    )

    cursor = (
        comments_collection
        .find(
            {
                "post_id": post_object_id,
                "parent_comment_id": None,
            }
        )
        .sort("created_at", 1)
        .limit(limit)
    )

    return await cursor.to_list(
        length=limit
    )


async def get_comment_replies(
    comment_id: str,
    limit: int = 50,
):
    comment_object_id = get_object_id(
        comment_id,
        "comment",
    )

    cursor = (
        comments_collection
        .find(
            {
                "parent_comment_id": comment_object_id
            }
        )
        .sort("created_at", 1)
        .limit(limit)
    )

    return await cursor.to_list(
        length=limit
    )


async def get_comments_by_user(
    user_id: str,
    limit: int = 50,
):
    user_object_id = get_object_id(
        user_id,
        "user",
    )

    cursor = (
        comments_collection
        .find(
            {
                "author_id": user_object_id
            }
        )
        .sort("created_at", -1)
        .limit(limit)
    )

    return await cursor.to_list(
        length=limit
    )


async def update_comment(
    comment_id: str,
    content: str,
):
    comment_object_id = get_object_id(
        comment_id,
        "comment",
    )

    current = await comments_collection.find_one(
        {"_id": comment_object_id}
    )

    if current is None:
        return None

    validated = CommentData(
        content=content,
    )

    await comments_collection.update_one(
        {"_id": comment_object_id},
        {
            "$set": {
                "content": validated.content,
                "updated_at": datetime.now(
                    timezone.utc
                ),
            }
        },
    )

    return await comments_collection.find_one(
        {"_id": comment_object_id}
    )


async def delete_comment(
    comment_id: str,
):
    comment_object_id = get_object_id(
        comment_id,
        "comment",
    )

    current = await comments_collection.find_one(
        {"_id": comment_object_id}
    )

    if current is None:
        return None

    post_id = current["post_id"]
    parent_comment_id = current.get("parent_comment_id")


    if parent_comment_id is None:

        replies_result = await comments_collection.delete_many(
            {
                "parent_comment_id": comment_object_id,
                "post_id": post_id,
            }
        )

        replies_deleted = replies_result.deleted_count

    else:
        replies_deleted = 0


    result = await comments_collection.delete_one(
        {"_id": comment_object_id}
    )

    if result.deleted_count == 0:
        return None


    comments_removed = 1 + replies_deleted

    await database.posts.update_one(
        {"_id": post_id},
        {
            "$inc": {
                "stats.comments_count": -comments_removed
            }
        },
    )


    if parent_comment_id is not None:

        await comments_collection.update_one(
            {"_id": parent_comment_id},
            {
                "$inc": {
                    "stats.replies_count": -1
                }
            },
        )

    return current