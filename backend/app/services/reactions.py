from typing import Optional

from app.database import reactions as reactions_db


VALID_TARGET_TYPES = {
    "POST",
    "COMMENT",
}

VALID_REACTIONS = {
    "UPVOTE",
    "DOWNVOTE",
}


class ReactionServiceError(Exception):
    """Base exception for reaction service errors."""


class InvalidReactionError(ReactionServiceError):
    """Raised when reaction input is invalid."""


class ReactionNotFoundError(ReactionServiceError):
    """Raised when a reaction does not exist."""


def _validate_target_type(target_type: str) -> str:
    if not isinstance(target_type, str):
        raise InvalidReactionError(
            "Target type must be a string."
        )

    target_type = target_type.strip().upper()

    if target_type not in VALID_TARGET_TYPES:
        raise InvalidReactionError(
            "Invalid reaction target type."
        )

    return target_type


def _validate_reaction(reaction: str) -> str:
    if not isinstance(reaction, str):
        raise InvalidReactionError(
            "Reaction must be a string."
        )

    reaction = reaction.strip().upper()

    if reaction not in VALID_REACTIONS:
        raise InvalidReactionError(
            "Invalid reaction type."
        )

    return reaction


def _validate_required_id(
    value: str,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise InvalidReactionError(
            f"{field_name} must be a string."
        )

    value = value.strip()

    if not value:
        raise InvalidReactionError(
            f"{field_name} is required."
        )

    return value


async def set_reaction(
    *,
    user_id: str,
    target_type: str,
    target_id: str,
    reaction: str,
):
    user_id = _validate_required_id(
        user_id,
        "User ID",
    )

    target_id = _validate_required_id(
        target_id,
        "Target ID",
    )

    target_type = _validate_target_type(
        target_type
    )

    reaction = _validate_reaction(
        reaction
    )

    result = await reactions_db.set_reaction(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        reaction=reaction,
    )

    if result is None:
        raise ReactionNotFoundError(
            f"{target_type.title()} not found."
        )

    return result


async def remove_reaction(
    *,
    user_id: str,
    target_type: str,
    target_id: str,
):
    user_id = _validate_required_id(
        user_id,
        "User ID",
    )

    target_id = _validate_required_id(
        target_id,
        "Target ID",
    )

    target_type = _validate_target_type(
        target_type
    )

    removed = await reactions_db.remove_reaction(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
    )

    if not removed:
        raise ReactionNotFoundError(
            "Reaction not found."
        )

    return True


async def get_user_reaction(
    *,
    user_id: str,
    target_type: str,
    target_id: str,
):
    user_id = _validate_required_id(
        user_id,
        "User ID",
    )

    target_id = _validate_required_id(
        target_id,
        "Target ID",
    )

    target_type = _validate_target_type(
        target_type
    )

    return await reactions_db.get_user_reaction(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
    )


async def get_reaction_counts(
    *,
    target_type: str,
    target_id: str,
):
    target_id = _validate_required_id(
        target_id,
        "Target ID",
    )

    target_type = _validate_target_type(
        target_type
    )

    return await reactions_db.get_reaction_counts(
        target_type=target_type,
        target_id=target_id,
    )