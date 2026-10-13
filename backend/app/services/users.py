from typing import Optional

from app.database import users as users_db
from pymongo.errors import DuplicateKeyError
from app.database.validation import UserData
from app.utils import get_object_id


MAX_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 254
MAX_PHONE_LENGTH = 30


class UserServiceError(Exception):
    pass


class InvalidUserError(UserServiceError):
    pass


class UserNotFoundError(UserServiceError):
    pass


class DuplicateUserError(UserServiceError):
    pass


def _validate_id(user_id: str) -> str:
    if not isinstance(user_id, str):
        raise InvalidUserError("User ID must be a string.")

    user_id = user_id.strip()

    if not user_id:
        raise InvalidUserError("User ID is required.")

    try:
        get_object_id(user_id, "user")
    except Exception as exc:
        raise InvalidUserError("Invalid user ID.") from exc

    return user_id


def _validate_user_data(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    google_id: Optional[str] = None,
):
    try:
        return UserData(
            name=name,
            email=email,
            phone=phone,
            google_id=google_id,
        )
    except ValueError as exc:
        raise InvalidUserError(str(exc)) from exc


async def create_user(
    *,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    google_id: Optional[str] = None,
):
    user_data = _validate_user_data(
        name=name,
        email=email,
        phone=phone,
        google_id=google_id,
    )

    if user_data.email:
        existing_user = await users_db.get_user_by_email(
            user_data.email
        )

        if existing_user is not None:
            raise DuplicateUserError(
                "A user with this email already exists."
            )

    if user_data.phone:
        existing_user = await users_db.get_user_by_phone(
            user_data.phone
        )

        if existing_user is not None:
            raise DuplicateUserError(
                "A user with this phone number already exists."
            )

    if user_data.google_id:
        existing_user = await users_db.get_user_by_google_id(
            user_data.google_id
        )

        if existing_user is not None:
            raise DuplicateUserError(
                "A user with this Google ID already exists."
            )

    try:
        user = await users_db.create_user(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            google_id=user_data.google_id,
        )
    except DuplicateKeyError as exc:
        raise DuplicateUserError(
            "A user with one of these credentials already exists."
        ) from exc

    if user is None:
        raise UserServiceError("Unable to create user.")

    return user

async def get_user(*, user_id: str):
    user_id = _validate_id(user_id)

    user = await users_db.get_user_by_id(user_id)

    if user is None:
        raise UserNotFoundError("User not found.")

    return user


async def get_user_by_email(*, email: str):
    if not isinstance(email, str):
        raise InvalidUserError("Email must be a string.")

    email = email.strip().lower()

    if not email:
        raise InvalidUserError("Email is required.")

    if len(email) > MAX_EMAIL_LENGTH:
        raise InvalidUserError(
            f"Email cannot exceed {MAX_EMAIL_LENGTH} characters."
        )

    user = await users_db.get_user_by_email(email)

    if user is None:
        raise UserNotFoundError("User not found.")

    return user


async def get_user_by_phone(*, phone: str):
    if not isinstance(phone, str):
        raise InvalidUserError("Phone number must be a string.")

    phone = phone.strip()

    if not phone:
        raise InvalidUserError("Phone number is required.")

    if len(phone) > MAX_PHONE_LENGTH:
        raise InvalidUserError(
            f"Phone number cannot exceed {MAX_PHONE_LENGTH} characters."
        )

    user = await users_db.get_user_by_phone(phone)

    if user is None:
        raise UserNotFoundError("User not found.")

    return user


async def get_user_by_google_id(*, google_id: str):
    if not isinstance(google_id, str):
        raise InvalidUserError("Google ID must be a string.")

    google_id = google_id.strip()

    if not google_id:
        raise InvalidUserError("Google ID is required.")

    user = await users_db.get_user_by_google_id(google_id)

    if user is None:
        raise UserNotFoundError("User not found.")

    return user


async def update_user(
    *,
    user_id: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
):
    user_id = _validate_id(user_id)

    current_user = await users_db.get_user_by_id(user_id)

    if current_user is None:
        raise UserNotFoundError("User not found.")

    updates = {}

    if name is not None:
        validated_name = _validate_user_data(
            name=name
        )
        updates["name"] = validated_name.name

    if email is not None:
        email = email.strip().lower()

        if not email:
            raise InvalidUserError("Email cannot be empty.")

        if len(email) > MAX_EMAIL_LENGTH:
            raise InvalidUserError(
                f"Email cannot exceed {MAX_EMAIL_LENGTH} characters."
            )

        existing_user = await users_db.get_user_by_email(email)

        if (
            existing_user is not None
            and str(existing_user["_id"]) != user_id
        ):
            raise DuplicateUserError(
                "A user with this email already exists."
            )

        updates["email"] = email

    if phone is not None:
        phone = phone.strip()

        if not phone:
            raise InvalidUserError("Phone number cannot be empty.")

        if len(phone) > MAX_PHONE_LENGTH:
            raise InvalidUserError(
                f"Phone number cannot exceed {MAX_PHONE_LENGTH} characters."
            )

        existing_user = await users_db.get_user_by_phone(phone)

        if (
            existing_user is not None
            and str(existing_user["_id"]) != user_id
        ):
            raise DuplicateUserError(
                "A user with this phone number already exists."
            )

        updates["phone"] = phone

    if not updates:
        return current_user

    updated_user = await users_db.update_user(
        user_id=user_id,
        updates=updates,
    )

    if updated_user is None:
        raise UserNotFoundError("User not found.")

    return updated_user