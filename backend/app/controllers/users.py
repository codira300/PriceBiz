from typing import Optional

from app.services import users as users_service


def serialize_user(user: dict):
    return {
        "_id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "phone": user.get("phone"),
    }


async def create_user(
    *,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    google_id: Optional[str] = None,
):
    user = await users_service.create_user(
        name=name,
        email=email,
        phone=phone,
        google_id=google_id,
    )

    return serialize_user(user)


async def get_user(
    *,
    user_id: str,
):
    user = await users_service.get_user(
        user_id=user_id,
    )

    return serialize_user(user)


async def get_user_by_email(
    *,
    email: str,
):
    user = await users_service.get_user_by_email(
        email=email,
    )

    return serialize_user(user)


async def get_user_by_phone(
    *,
    phone: str,
):
    user = await users_service.get_user_by_phone(
        phone=phone,
    )

    return serialize_user(user)


async def get_user_by_google_id(
    *,
    google_id: str,
):
    user = await users_service.get_user_by_google_id(
        google_id=google_id,
    )

    return serialize_user(user)


async def update_user(
    *,
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
):
    user = await users_service.update_user(
        user_id=user_id,
        name=name,
        email=email,
        phone=phone,
    )

    return serialize_user(user)