from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.controllers import comments as comments_controller
from app.services import comments as comments_service


router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


class CreateCommentRequest(BaseModel):
    post_id: str = Field(..., min_length=1)
    author_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    parent_comment_id: Optional[str] = None


class UpdateCommentRequest(BaseModel):
    author_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    request: CreateCommentRequest,
):
    try:
        return await comments_controller.create_comment(
            post_id=request.post_id,
            author_id=request.author_id,
            content=request.content,
            parent_comment_id=request.parent_comment_id,
        )

    except comments_service.InvalidCommentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except comments_service.CommentServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get("/post/{post_id}")
async def get_post_comments(
    post_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):
    try:
        return await comments_controller.get_post_comments(
            post_id=post_id,
            limit=limit,
        )

    except comments_service.InvalidCommentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/user/{user_id}")
async def get_user_comments(
    user_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):
    try:
        return await comments_controller.get_user_comments(
            user_id=user_id,
            limit=limit,
        )

    except comments_service.InvalidCommentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/{comment_id}/replies")
async def get_comment_replies(
    comment_id: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):
    try:
        return await comments_controller.get_comment_replies(
            comment_id=comment_id,
            limit=limit,
        )

    except comments_service.CommentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except comments_service.InvalidCommentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/{comment_id}")
async def get_comment(
    comment_id: str,
):
    try:
        return await comments_controller.get_comment(
            comment_id=comment_id,
        )

    except comments_service.CommentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except comments_service.InvalidCommentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch("/{comment_id}")
async def update_comment(
    comment_id: str,
    request: UpdateCommentRequest,
):
    try:
        return await comments_controller.update_comment(
            comment_id=comment_id,
            author_id=request.author_id,
            content=request.content,
        )

    except comments_service.CommentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except comments_service.CommentAuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    except comments_service.InvalidCommentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    author_id: str = Query(...),
):
    try:
        await comments_controller.delete_comment(
            comment_id=comment_id,
            author_id=author_id,
        )

        return {
            "message": "Comment deleted successfully."
        }

    except comments_service.CommentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except comments_service.CommentAuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    except comments_service.InvalidCommentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )