from typing import Optional

from app.database.connection import database
from app.utils import get_object_id


users_collection = database.users


async def create_user(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    google_id: Optional[str] = None,
    password_hash: Optional[str] = None,
):
    user = {
        "name": name,
        "email": email,
        "phone": phone,
        "auth": {
            "google_id": google_id,
            "password_hash": password_hash,
        },
    }

    result = await users_collection.insert_one(user)

    return await users_collection.find_one(
        {"_id": result.inserted_id}
    )


async def get_user_by_id(user_id: str):
    user_object_id = get_object_id(
        user_id,
        "user",
    )

    return await users_collection.find_one(
        {"_id": user_object_id}
    )


async def get_user_by_email(email: str):
    return await users_collection.find_one(
        {"email": email}
    )


async def get_user_by_phone(phone: str):
    return await users_collection.find_one(
        {"phone": phone}
    )


async def get_user_by_google_id(google_id: str):
    return await users_collection.find_one(
        {"auth.google_id": google_id}
    )


async def update_user(
    user_id: str,
    updates: dict,
):
    user_object_id = get_object_id(
        user_id,
        "user",
    )

    await users_collection.update_one(
        {"_id": user_object_id},
        {"$set": updates},
    )

    return await get_user_by_id(user_id)