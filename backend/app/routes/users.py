from typing import Optional

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field

from app.controllers import users as users_controller


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


class CreateUserRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    email: Optional[str] = Field(
        default=None,
        max_length=254,
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=30,
    )
    google_id: Optional[str] = Field(
        default=None,
        min_length=1,
    )


class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    email: Optional[str] = Field(
        default=None,
        max_length=254,
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=30,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: CreateUserRequest,
):
    return await users_controller.create_user(
        name=request.name,
        email=request.email,
        phone=request.phone,
        google_id=request.google_id,
    )


@router.get("/email")
async def get_user_by_email(
    email: str = Query(...),
):
    return await users_controller.get_user_by_email(
        email=email,
    )


@router.get("/phone")
async def get_user_by_phone(
    phone: str = Query(...),
):
    return await users_controller.get_user_by_phone(
        phone=phone,
    )


@router.get("/google")
async def get_user_by_google_id(
    google_id: str = Query(...),
):
    return await users_controller.get_user_by_google_id(
        google_id=google_id,
    )


@router.get("/{user_id}")
async def get_user(
    user_id: str,
):
    return await users_controller.get_user(
        user_id=user_id,
    )


@router.patch("/{user_id}")
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
):
    return await users_controller.update_user(
        user_id=user_id,
        name=request.name,
        email=request.email,
        phone=request.phone,
    )