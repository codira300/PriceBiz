import hashlib
import secrets
import uuid

from datetime import datetime, timedelta, timezone

import jwt
import logging

from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHash,
    VerificationError,
    VerifyMismatchError,
)

from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    GOOGLE_CLIENT_ID,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

from app.monitoring.metrics import (
    AUTH_EVENTS_TOTAL,
    AUTH_FAILURES_TOTAL,
)

from app.database import users as users_db
from app.database.connection import database
from app.utils import get_object_id

logger = logging.getLogger("pricebiz")

password_hasher = PasswordHasher()


class AuthServiceError(Exception):
    pass


class InvalidCredentialsError(AuthServiceError):
    pass


class EmailAlreadyExistsError(AuthServiceError):
    pass


class GoogleAuthenticationError(AuthServiceError):
    pass


class InvalidTokenError(AuthServiceError):
    pass


class InvalidRefreshTokenError(AuthServiceError):
    pass


class RefreshTokenReuseError(AuthServiceError):
    pass


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    try:
        return password_hasher.verify(
            password_hash,
            password,
        )
    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHash
    ):
        return False


def create_access_token(
    user_id: str,
) -> str:
    now = datetime.now(timezone.utc)

    expires_at = (
        now
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": user_id,
        "iat": now,
        "exp": expires_at,
        "type": "access",
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError(
            "Authentication token has expired"
        )
    except jwt.InvalidTokenError:
        raise InvalidTokenError(
            "Invalid authentication token"
        )

    if payload.get("type") != "access":
        raise InvalidTokenError(
            "Invalid authentication token type"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise InvalidTokenError(
            "Authentication token does not contain a user ID"
        )

    return payload


async def register_user(
    name: str,
    email: str,
    password: str,
):
    email = email.strip().lower()

    existing_user = (
        await users_db.get_user_by_email(
            email
        )
    )

    if existing_user:
        AUTH_FAILURES_TOTAL.labels(
            method="register",
            reason="email_already_exists",
        ).inc()

        logger.warning(
            "Registration failed | reason=email_already_exists"
        )

        raise EmailAlreadyExistsError(
            "A user with this email already exists"
        )

    password_hash = hash_password(
        password
    )

    user = await users_db.create_user(
        name=name,
        email=email,
        password_hash=password_hash,
    )
    
    AUTH_EVENTS_TOTAL.labels(
        event="register_success",
    ).inc()

    logger.info(
        "Registration successful"
    )

    return user


async def login_user(
    email: str,
    password: str,
):
    email = email.strip().lower()

    user = await users_db.get_user_by_email(
        email
    )

    if not user:
        AUTH_FAILURES_TOTAL.labels(
            method="login",
            reason="invalid_credentials",
        ).inc()
        
        logger.warning(
            "Login failed | reason=invalid_credentials"
        )
        
        raise InvalidCredentialsError(
            "Invalid email or password"
        )

    auth = user.get("auth") or {}

    password_hash = auth.get(
        "password_hash"
    )

    if not password_hash:
        AUTH_FAILURES_TOTAL.labels(
            method="login",
            reason="authentication_method_mismatch",
        ).inc()

        logger.warning(
            "Login failed | reason=authentication_method_mismatch"
        )

        raise InvalidCredentialsError(
            "This account does not use email/password authentication"
        )

    if not verify_password(
        password,
        password_hash,
    ):
        AUTH_FAILURES_TOTAL.labels(
            method="login",
            reason="invalid_credentials",
        ).inc()

        logger.warning(
            "Login failed | reason=invalid_credentials"
        )

        raise InvalidCredentialsError(
            "Invalid email or password"
        )
        
    AUTH_EVENTS_TOTAL.labels(
        event="login_success",
    ).inc()

    logger.info(
        "Login successful"
    )

    return user


async def authenticate_google_user(
    credential: str,
):
    if not GOOGLE_CLIENT_ID:
        AUTH_FAILURES_TOTAL.labels(
            method="google",
            reason="not_configured",
        ).inc()

        logger.error(
            "Google authentication failed | reason=not_configured"
        )

        raise GoogleAuthenticationError(
            "Google authentication is not configured"
        )

    try:
        google_user = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except (
        ValueError,
        GoogleAuthError,
    ):
        AUTH_FAILURES_TOTAL.labels(
            method="google",
            reason="invalid_credential",
        ).inc()

        logger.warning(
            "Google authentication failed | reason=invalid_credential"
        )

        raise GoogleAuthenticationError(
            "Invalid Google authentication credential"
        )

    google_id = google_user.get("sub")
    email = google_user.get("email")
    name = google_user.get("name")

    if not google_id or not email:
        AUTH_FAILURES_TOTAL.labels(
            method="google",
            reason="incomplete_account_information",
        ).inc()

        logger.warning(
            "Google authentication failed | "
            "reason=incomplete_account_information"
        )

        raise GoogleAuthenticationError(
            "Google account information is incomplete"
        )

    existing_user = (
        await users_db.get_user_by_google_id(
            google_id
        )
    )

    if existing_user:
        AUTH_EVENTS_TOTAL.labels(
            event="google_login_success",
        ).inc()

        logger.info(
            "Google authentication successful | account=existing_google_account"
        )

        return existing_user

    existing_email_user = (
        await users_db.get_user_by_email(
            email.lower()
        )
    )

    if existing_email_user:
        await users_db.update_user(
            str(existing_email_user["_id"]),
            {
                "auth.google_id": google_id,
            },
        )

        AUTH_EVENTS_TOTAL.labels(
            event="google_login_success",
        ).inc()

        logger.info(
            "Google authentication successful | account=linked_existing_account"
        )

        return await users_db.get_user_by_id(
            str(existing_email_user["_id"])
        )

    user = await users_db.create_user(
        name=name or email.split("@")[0],
        email=email.lower(),
        google_id=google_id,
    )

    AUTH_EVENTS_TOTAL.labels(
        event="google_login_success",
    ).inc()

    logger.info(
        "Google authentication successful | account=new_account"
    )

    return user


def _ensure_utc_datetime(value: datetime) -> datetime:
    """Normalize a datetime from MongoDB to timezone-aware UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _hash_refresh_token(
    token: str,
) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def _generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


async def _create_refresh_token(
    user_id: str,
    family_id: str | None = None,
):
    user_object_id = get_object_id(
        user_id,
        "user",
    )

    now = datetime.now(timezone.utc)

    expires_at = (
        now
        + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    raw_token = _generate_refresh_token()

    token_hash = _hash_refresh_token(
        raw_token
    )

    if family_id is None:
        family_id = str(uuid.uuid4())

    token_document = {
        "token_hash": token_hash,
        "user_id": user_object_id,
        "family_id": family_id,
        "expires_at": expires_at,
        "created_at": now,
        "revoked_at": None,
        "replaced_by": None,
    }

    result = await database.refresh_tokens.insert_one(
        token_document
    )

    return {
        "token": raw_token,
        "token_id": result.inserted_id,
        "family_id": family_id,
    }


async def create_session(
    user_id: str,
):
    access_token = create_access_token(
        user_id
    )

    refresh_token = await _create_refresh_token(
        user_id
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token["token"],
        "token_type": "bearer",
    }


async def refresh_session(
    refresh_token: str,
):
    refresh_token = refresh_token.strip()

    if not refresh_token:
        AUTH_FAILURES_TOTAL.labels(
            method="refresh",
            reason="empty_token",
        ).inc()

        raise InvalidRefreshTokenError(
            "Refresh token cannot be empty"
        )

    token_hash = _hash_refresh_token(
        refresh_token
    )

    token_document = (
        await database.refresh_tokens.find_one(
            {
                "token_hash": token_hash,
            }
        )
    )

    if token_document is None:
        AUTH_FAILURES_TOTAL.labels(
            method="refresh",
            reason="invalid_token",
        ).inc()

        logger.warning(
            "Refresh failed | reason=invalid_token"
        )

        raise InvalidRefreshTokenError(
            "Invalid refresh token"
        )

    now = datetime.now(timezone.utc)

    if token_document.get("revoked_at") is not None:
        await database.refresh_tokens.update_many(
            {
                "family_id": token_document["family_id"],
                "revoked_at": None,
            },
            {
                "$set": {
                    "revoked_at": now,
                }
            },
        )

        AUTH_FAILURES_TOTAL.labels(
            method="refresh",
            reason="token_reuse",
        ).inc()

        AUTH_EVENTS_TOTAL.labels(
            event="refresh_reuse_detected",
        ).inc()

        logger.warning(
            "Refresh token reuse detected"
        )

        raise RefreshTokenReuseError(
            "Refresh token reuse detected"
        )

    expires_at = _ensure_utc_datetime(
        token_document["expires_at"]
    )

    if expires_at <= now:
        await database.refresh_tokens.update_one(
            {
                "_id": token_document["_id"],
                "revoked_at": None,
            },
            {
                "$set": {
                    "revoked_at": now,
                }
            },
        )

        AUTH_FAILURES_TOTAL.labels(
            method="refresh",
            reason="expired_token",
        ).inc()

        logger.warning(
            "Refresh failed | reason=expired_token"
        )

        raise InvalidRefreshTokenError(
            "Refresh token has expired"
        )

    user = await users_db.get_user_by_id(
        str(token_document["user_id"])
    )

    if user is None:
        await database.refresh_tokens.update_one(
            {
                "_id": token_document["_id"],
                "revoked_at": None,
            },
            {
                "$set": {
                    "revoked_at": now,
                }
            },
        )

        AUTH_FAILURES_TOTAL.labels(
            method="refresh",
            reason="user_not_found",
        ).inc()

        logger.warning(
            "Refresh failed | reason=user_not_found"
        )

        raise InvalidRefreshTokenError(
            "Authenticated user no longer exists"
        )

    replacement = await _create_refresh_token(
        user_id=str(
            token_document["user_id"]
        ),
        family_id=token_document["family_id"],
    )

    result = await database.refresh_tokens.update_one(
        {
            "_id": token_document["_id"],
            "revoked_at": None,
        },
        {
            "$set": {
                "revoked_at": now,
                "replaced_by": replacement["token_id"],
            }
        },
    )

    if result.modified_count != 1:
        await database.refresh_tokens.update_one(
            {
                "_id": replacement["token_id"],
                "revoked_at": None,
            },
            {
                "$set": {
                    "revoked_at": now,
                }
            },
        )

        await database.refresh_tokens.update_many(
            {
                "family_id": token_document["family_id"],
                "revoked_at": None,
            },
            {
                "$set": {
                    "revoked_at": now,
                }
            },
        )

        AUTH_FAILURES_TOTAL.labels(
            method="refresh",
            reason="token_reuse",
        ).inc()

        AUTH_EVENTS_TOTAL.labels(
            event="refresh_reuse_detected",
        ).inc()

        logger.warning(
            "Refresh token reuse detected during rotation"
        )

        raise RefreshTokenReuseError(
            "Refresh token reuse detected"
        )

    access_token = create_access_token(
        str(user["_id"])
    )

    AUTH_EVENTS_TOTAL.labels(
        event="refresh_success",
    ).inc()

    logger.info(
        "Refresh successful"
    )

    return {
        "access_token": access_token,
        "refresh_token": replacement["token"],
        "token_type": "bearer",
    }
    
    
    
async def revoke_refresh_token(
    refresh_token: str,
):
    refresh_token = refresh_token.strip()

    if not refresh_token:
        return

    token_hash = _hash_refresh_token(
        refresh_token
    )

    await database.refresh_tokens.update_one(
        {
            "token_hash": token_hash,
            "revoked_at": None,
        },
        {
            "$set": {
                "revoked_at": datetime.now(
                    timezone.utc
                ),
            }
        },
    )

    AUTH_EVENTS_TOTAL.labels(
        event="logout",
    ).inc()

    logger.info(
        "Logout completed"
    )


async def revoke_all_user_refresh_tokens(
    user_id: str,
):
    user_object_id = get_object_id(
        user_id,
        "user",
    )

    await database.refresh_tokens.update_many(
        {
            "user_id": user_object_id,
            "revoked_at": None,
        },
        {
            "$set": {
                "revoked_at": datetime.now(
                    timezone.utc
                ),
            }
        },
    )