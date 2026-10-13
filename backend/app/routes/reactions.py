from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.controllers import reactions as reactions_controller
from app.services import reactions as reactions_service


router = APIRouter(
    prefix="/reactions",
    tags=["Reactions"],
)


class SetReactionRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    target_type: str = Field(..., min_length=1)
    target_id: str = Field(..., min_length=1)
    reaction: str = Field(..., min_length=1)


@router.put("")
async def set_reaction(
    request: SetReactionRequest,
):
    try:
        return await reactions_controller.set_reaction(
            user_id=request.user_id,
            target_type=request.target_type,
            target_id=request.target_id,
            reaction=request.reaction,
        )

    except reactions_service.ReactionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except reactions_service.InvalidReactionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete("")
async def remove_reaction(
    user_id: str = Query(...),
    target_type: str = Query(...),
    target_id: str = Query(...),
):
    try:
        return await reactions_controller.remove_reaction(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
        )

    except reactions_service.ReactionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except reactions_service.InvalidReactionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/user")
async def get_user_reaction(
    user_id: str = Query(...),
    target_type: str = Query(...),
    target_id: str = Query(...),
):
    try:
        return await reactions_controller.get_user_reaction(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
        )

    except reactions_service.InvalidReactionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/counts")
async def get_reaction_counts(
    target_type: str = Query(...),
    target_id: str = Query(...),
):
    try:
        return await reactions_controller.get_reaction_counts(
            target_type=target_type,
            target_id=target_id,
        )

    except reactions_service.InvalidReactionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )