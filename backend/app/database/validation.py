
import re
from datetime import datetime
from typing import Any, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class DatabaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def validate_new_password(password: str) -> str:
    """Validate the password policy for new registrations."""

    if not 12 <= len(password) <= 128:
        raise ValueError(
            "Password must be between 12 and 128 characters."
        )

    if any(char.isspace() for char in password):
        raise ValueError(
            "Password must not contain whitespace."
        )

    if not re.search(r"[A-Z]", password):
        raise ValueError(
            "Password must contain at least one uppercase letter."
        )

    if not re.search(r"[a-z]", password):
        raise ValueError(
            "Password must contain at least one lowercase letter."
        )

    if not re.search(r"[0-9]", password):
        raise ValueError(
            "Password must contain at least one number."
        )

    if not re.search(r"[^A-Za-z0-9\s]", password):
        raise ValueError(
            "Password must contain at least one special character."
        )

    return password


class UserData(DatabaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, max_length=254)
    phone: Optional[str] = Field(default=None, max_length=30)
    google_id: Optional[str] = Field(default=None, min_length=1)

    @field_validator("name", "email", "phone", "google_id")
    @classmethod
    def strip_strings(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        if value is None:
            return value

        return value.lower()


class ProductData(DatabaseModel):
    name: str = Field(min_length=1, max_length=200)
    brand: Optional[str] = Field(default=None, max_length=100)
    category: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("name", "brand", "category", "description")
    @classmethod
    def validate_strings(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value


class ProductVariantData(DatabaseModel):
    name: str = Field(min_length=1, max_length=200)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Variant name cannot be empty")

        return value


class LocationData(DatabaseModel):
    country: str = Field(min_length=1, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    lga: Optional[str] = Field(default=None, max_length=100)
    area: Optional[str] = Field(default=None, max_length=150)
    market: Optional[str] = Field(default=None, max_length=150)

    @field_validator("country", "state", "lga", "area", "market")
    @classmethod
    def validate_strings(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Location value cannot be empty")

        return value


class SourceData(DatabaseModel):
    name: str = Field(min_length=1, max_length=200)
    type: str = Field(min_length=1, max_length=50)
    url: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Source name cannot be empty")

        return value

    @field_validator("type")
    @classmethod
    def normalize_type(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Source type cannot be empty")

        return value.upper()


class PriceData(DatabaseModel):
    amount: int = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value):
        value = value.strip().upper()

        if not value:
            raise ValueError("Currency cannot be empty")

        return value


class PriceObservationData(DatabaseModel):
    price: PriceData
    observed_at: datetime
    seller_type: Optional[str] = Field(default=None, max_length=50)
    evidence: dict[str, Any] = Field(default_factory=dict)

    @field_validator("seller_type")
    @classmethod
    def normalize_seller_type(cls, value):
        if value is None:
            return value

        value = value.strip().upper()

        if not value:
            return None

        return value


class RawObservationData(DatabaseModel):
    input_format: str = Field(min_length=1, max_length=100)
    payload: dict[str, Any]
    processing_status: str = Field(
        default="PENDING",
        min_length=1,
        max_length=50,
    )

    @field_validator("input_format", "processing_status")
    @classmethod
    def validate_strings(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value.upper()


class CommentData(DatabaseModel):
    content: str = Field(min_length=1, max_length=1000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Comment content cannot be empty")

        return value


class RegisterData(DatabaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("name", "email")
    @classmethod
    def validate_strings(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        return validate_new_password(value)


class LoginData(DatabaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Email cannot be empty")

        return value.lower()


class GoogleAuthData(DatabaseModel):
    credential: str = Field(min_length=1)

    @field_validator("credential")
    @classmethod
    def validate_credential(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Google credential cannot be empty")

        return value


class RefreshTokenData(DatabaseModel):
    refresh_token: str = Field(min_length=1, max_length=1000)

    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Refresh token cannot be empty")

        return value
