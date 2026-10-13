from datetime import datetime, timezone

from app.database.connection import database
from app.utils import get_object_id


reactions_collection = database.reactions


VALID_TARGET_TYPES = {
    "POST",
    "COMMENT",
}

VALID_REACTIONS = {
    "UPVOTE",
    "DOWNVOTE",
}


async def set_reaction(
    user_id: str,
    target_type: str,
    target_id: str,
    reaction: str,
):
    user_object_id = get_object_id(
        user_id,
        "user",
    )

    target_type = target_type.upper()
    reaction = reaction.upper()

    if target_type not in VALID_TARGET_TYPES:
        raise ValueError(
            "Invalid reaction target type"
        )

    if reaction not in VALID_REACTIONS:
        raise ValueError(
            "Invalid reaction type"
        )

    # Validate that the target exists
    if target_type == "POST":
        target_object_id = get_object_id(
            target_id,
            "post",
        )

        target = await database.posts.find_one(
            {"_id": target_object_id}
        )

    else:
        target_object_id = get_object_id(
            target_id,
            "comment",
        )

        target = await database.comments.find_one(
            {"_id": target_object_id}
        )

    if target is None:
        return None

    # Check whether this user has already reacted
    existing = await reactions_collection.find_one(
        {
            "user_id": user_object_id,
            "target_type": target_type,
            "target_id": target_object_id,
        }
    )

    now = datetime.now(timezone.utc)

    # User already has a reaction
    if existing:

        old_reaction = existing["reaction"]

        # Same reaction: nothing needs to change
        if old_reaction == reaction:
            return existing

        # Change the reaction
        await reactions_collection.update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "reaction": reaction,
                    "updated_at": now,
                }
            },
        )

        # Remove the old reaction from the target statistics
        await _update_target_stats(
            target_type,
            target_object_id,
            old_reaction,
            -1,
        )

        # Add the new reaction to the target statistics
        await _update_target_stats(
            target_type,
            target_object_id,
            reaction,
            1,
        )

        return await reactions_collection.find_one(
            {"_id": existing["_id"]}
        )

    # User does not have a reaction yet
    reaction_document = {
        "user_id": user_object_id,
        "target_type": target_type,
        "target_id": target_object_id,
        "reaction": reaction,
        "created_at": now,
        "updated_at": now,
    }

    result = await reactions_collection.insert_one(
        reaction_document
    )

    # Increment target statistics
    await _update_target_stats(
        target_type,
        target_object_id,
        reaction,
        1,
    )

    return await reactions_collection.find_one(
        {"_id": result.inserted_id}
    )


async def remove_reaction(
    user_id: str,
    target_type: str,
    target_id: str,
):
    user_object_id = get_object_id(
        user_id,
        "user",
    )

    target_type = target_type.upper()

    if target_type not in VALID_TARGET_TYPES:
        raise ValueError(
            "Invalid reaction target type"
        )

    target_object_id = get_object_id(
        target_id,
        target_type.lower(),
    )

    existing = await reactions_collection.find_one(
        {
            "user_id": user_object_id,
            "target_type": target_type,
            "target_id": target_object_id,
        }
    )

    if existing is None:
        return False

    await reactions_collection.delete_one(
        {"_id": existing["_id"]}
    )

    # Decrease the corresponding target statistic
    await _update_target_stats(
        target_type,
        target_object_id,
        existing["reaction"],
        -1,
    )

    return True


async def get_user_reaction(
    user_id: str,
    target_type: str,
    target_id: str,
):
    user_object_id = get_object_id(
        user_id,
        "user",
    )

    target_type = target_type.upper()

    if target_type not in VALID_TARGET_TYPES:
        raise ValueError(
            "Invalid reaction target type"
        )

    target_object_id = get_object_id(
        target_id,
        target_type.lower(),
    )

    return await reactions_collection.find_one(
        {
            "user_id": user_object_id,
            "target_type": target_type,
            "target_id": target_object_id,
        }
    )


async def get_reaction_counts(
    target_type: str,
    target_id: str,
):
    target_type = target_type.upper()

    if target_type not in VALID_TARGET_TYPES:
        raise ValueError(
            "Invalid reaction target type"
        )

    target_object_id = get_object_id(
        target_id,
        target_type.lower(),
    )

    counts = {
        "UPVOTE": 0,
        "DOWNVOTE": 0,
    }

    cursor = reactions_collection.find(
        {
            "target_type": target_type,
            "target_id": target_object_id,
        }
    )

    reactions = await cursor.to_list(length=None)

    for reaction in reactions:
        reaction_type = reaction["reaction"]

        if reaction_type in counts:
            counts[reaction_type] += 1

    return counts


async def _update_target_stats(
    target_type: str,
    target_id,
    reaction: str,
    amount: int,
):
    if reaction == "UPVOTE":
        field = "stats.upvotes"
    else:
        field = "stats.downvotes"

    collection = (
        database.posts
        if target_type == "POST"
        else database.comments
    )

    await collection.update_one(
        {"_id": target_id},
        {
            "$inc": {
                field: amount,
            }
        },
    )