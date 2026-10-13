from app.services import reactions as reactions_service


async def set_reaction(
    *,
    user_id: str,
    target_type: str,
    target_id: str,
    reaction: str,
):
    return await reactions_service.set_reaction(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        reaction=reaction,
    )


async def remove_reaction(
    *,
    user_id: str,
    target_type: str,
    target_id: str,
):
    await reactions_service.remove_reaction(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
    )

    return {
        "message": "Reaction removed successfully."
    }


async def get_user_reaction(
    *,
    user_id: str,
    target_type: str,
    target_id: str,
):
    reaction = await reactions_service.get_user_reaction(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
    )

    if reaction is None:
        return {
            "reaction": None
        }

    return reaction


async def get_reaction_counts(
    *,
    target_type: str,
    target_id: str,
):
    return await reactions_service.get_reaction_counts(
        target_type=target_type,
        target_id=target_id,
    )