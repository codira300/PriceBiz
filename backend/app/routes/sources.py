from typing import Any, Optional

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field

from app.controllers import sources as sources_controller


router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)


class CreateSourceRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    source_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    url: Optional[str] = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class UpdateSourceRequest(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    source_type: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    url: Optional[str] = None

    metadata: Optional[dict[str, Any]] = None


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_source(
    request: CreateSourceRequest,
):
    return await sources_controller.create_source(
        name=request.name,
        source_type=request.source_type,
        url=request.url,
        metadata=request.metadata,
    )


@router.get("")
async def find_sources(
    source_type: Optional[str] = Query(
        default=None,
    ),
    name: Optional[str] = Query(
        default=None,
    ),
):
    return await sources_controller.find_sources(
        source_type=source_type,
        name=name,
    )


@router.get("/{source_id}")
async def get_source(
    source_id: str,
):
    return await sources_controller.get_source(
        source_id=source_id,
    )


@router.patch("/{source_id}")
async def update_source(
    source_id: str,
    request: UpdateSourceRequest,
):
    return await sources_controller.update_source(
        source_id=source_id,
        name=request.name,
        source_type=request.source_type,
        url=request.url,
        metadata=request.metadata,
    )