from bson import ObjectId
from fastapi import HTTPException


def get_object_id(value: str, resource: str):
    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {resource} ID"
        )

    return ObjectId(value)