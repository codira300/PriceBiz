from typing import Any, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from app.controllers import posts as posts_controller


router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


def serialize_post(data: Any) -> Any:
    """Convert MongoDB documents into JSON-compatible data."""
    return jsonable_encoder(
        data,
        custom_encoder={
            ObjectId: str,
        },
    )


class CreatePostRequest(BaseModel):
    author_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    post_type: str = "GENERAL"
    product_id: Optional[str] = None
    variant_id: Optional[str] = None
    location_id: Optional[str] = None


class UpdatePostRequest(BaseModel):
    author_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_post(request: CreatePostRequest):
    try:
        post = await posts_controller.create_post(
            author_id=request.author_id,
            content=request.content,
            post_type=request.post_type,
            product_id=request.product_id,
            variant_id=request.variant_id,
            location_id=request.location_id,
        )

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found.",
            )

        return serialize_post(post)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("")
async def list_posts(
    post_type: Optional[str] = None,
    product_id: Optional[str] = None,
    author_id: Optional[str] = None,
    location_id: Optional[str] = None,
    status_filter: str = Query(
        default="ACTIVE",
        alias="status",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
):
    try:
        posts = await posts_controller.list_posts(
            post_type=post_type,
            product_id=product_id,
            author_id=author_id,
            location_id=location_id,
            status=status_filter,
            limit=limit,
            skip=skip,
        )

        return serialize_post(posts)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/feed")
async def get_feed(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
):
    try:
        posts = await posts_controller.get_feed(
            limit=limit,
            skip=skip,
        )

        return serialize_post(posts)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/user/{user_id}")
async def get_posts_by_user(
    user_id: str,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    try:
        posts = await posts_controller.get_posts_by_user(
            user_id=user_id,
            limit=limit,
        )

        return serialize_post(posts)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/product/{product_id}")
async def get_posts_by_product(
    product_id: str,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    try:
        posts = await posts_controller.get_posts_by_product(
            product_id=product_id,
            limit=limit,
        )

        return serialize_post(posts)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/location/{location_id}")
async def get_posts_by_location(
    location_id: str,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    try:
        posts = await posts_controller.get_posts_by_location(
            location_id=location_id,
            limit=limit,
        )

        return serialize_post(posts)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{post_id}")
async def get_post(post_id: str):
    try:
        post = await posts_controller.get_post(
            post_id=post_id,
        )

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.",
            )

        return serialize_post(post)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch("/{post_id}")
async def update_post(
    post_id: str,
    request: UpdatePostRequest,
):
    try:
        post = await posts_controller.update_post(
            post_id=post_id,
            author_id=request.author_id,
            content=request.content,
        )

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.",
            )

        return serialize_post(post)

    except HTTPException:
        raise

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    author_id: str = Query(...),
):
    try:
        deleted = await posts_controller.delete_post(
            post_id=post_id,
            author_id=author_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.",
            )

        return {
            "message": "Post deleted successfully."
        }

    except HTTPException:
        raise

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch("/{post_id}/flag")
async def flag_post(post_id: str):
    try:
        post = await posts_controller.flag_post(
            post_id=post_id,
        )

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.",
            )

        return serialize_post(post)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch("/{post_id}/restore")
async def restore_post(post_id: str):
    try:
        post = await posts_controller.restore_post(
            post_id=post_id,
        )

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.",
            )

        return serialize_post(post)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch("/{post_id}/reject")
async def reject_post(post_id: str):
    try:
        post = await posts_controller.reject_post(
            post_id=post_id,
        )

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.",
            )

        return serialize_post(post)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc