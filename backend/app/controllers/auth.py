from app.services.auth import (
    authenticate_google_user,
    create_session,
    login_user,
    refresh_session,
    register_user,
    revoke_refresh_token,
)


def serialize_user(user: dict):
    return {
        "_id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "phone": user.get("phone"),
    }


async def register(
    name: str,
    email: str,
    password: str,
):
    user = await register_user(
        name=name,
        email=email,
        password=password,
    )

    session = await create_session(str(user["_id"]))

    return {
        "user": serialize_user(user),
        **session,
    }


async def login(
    email: str,
    password: str,
):
    user = await login_user(
        email=email,
        password=password,
    )

    session = await create_session(str(user["_id"]))

    return {
        "user": serialize_user(user),
        **session,
    }


async def google_login(credential: str):
    user = await authenticate_google_user(credential)

    session = await create_session(str(user["_id"]))

    return {
        "user": serialize_user(user),
        **session,
    }


async def refresh(refresh_token: str):
    return await refresh_session(refresh_token)


async def logout(refresh_token: str):
    await revoke_refresh_token(refresh_token)

    return {
        "message": "Logged out successfully"
    }


async def get_me(user: dict):
    return {
        "user": serialize_user(user)
    }