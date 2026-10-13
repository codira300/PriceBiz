from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.controllers import raw_observations as raw_observations_controller
from app.services import raw_observations as raw_observations_service


router = APIRouter(
    prefix="/raw-observations",
    tags=["Raw Observations"],
)


class CreateRawObservationRequest(BaseModel):
    input_format: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    payload: dict

    source_id: Optional[str] = Field(
        default=None,
        min_length=1,
    )


class UpdateProcessingStatusRequest(BaseModel):
    processing_status: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_raw_observation(
    request: CreateRawObservationRequest,
):
    try:
        return await raw_observations_controller.create_raw_observation(
            input_format=request.input_format,
            payload=request.payload,
            source_id=request.source_id,
        )

    except raw_observations_service.InvalidRawObservationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except raw_observations_service.UnsupportedInputFormatError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("")
async def find_raw_observations(
    input_format: Optional[str] = Query(
        default=None,
    ),
    processing_status: Optional[str] = Query(
        default=None,
    ),
    source_id: Optional[str] = Query(
        default=None,
    ),
):
    try:
        return await raw_observations_controller.find_raw_observations(
            input_format=input_format,
            processing_status=processing_status,
            source_id=source_id,
        )

    except raw_observations_service.InvalidRawObservationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except raw_observations_service.UnsupportedInputFormatError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("/{observation_id}")
async def get_raw_observation(
    observation_id: str,
):
    try:
        return await raw_observations_controller.get_raw_observation(
            observation_id=observation_id,
        )

    except raw_observations_service.RawObservationNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except raw_observations_service.InvalidRawObservationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.patch("/{observation_id}/status")
async def update_processing_status(
    observation_id: str,
    request: UpdateProcessingStatusRequest,
):
    try:
        return await raw_observations_controller.update_processing_status(
            observation_id=observation_id,
            processing_status=request.processing_status,
        )

    except raw_observations_service.RawObservationNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except raw_observations_service.InvalidRawObservationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/{observation_id}/process")
async def process_raw_observation(
    observation_id: str,
    creator_id: Optional[str] = Query(default=None),
    submitted_by: Optional[str] = Query(default=None),
):
    try:
        return await raw_observations_controller.process_raw_observation(
            observation_id=observation_id,
            creator_id=creator_id,
            submitted_by=submitted_by,
        )

    except raw_observations_service.RawObservationNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except raw_observations_service.InvalidRawObservationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except raw_observations_service.UnsupportedInputFormatError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except raw_observations_service.RawObservationProcessingError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/process-pending")
async def process_pending_raw_observations(
    input_format: Optional[str] = Query(default=None),
    creator_id: Optional[str] = Query(default=None),
    submitted_by: Optional[str] = Query(default=None),
):
    try:
        return await raw_observations_controller.queue_process_pending_raw_observations(
            input_format=input_format,
            creator_id=creator_id,
            submitted_by=submitted_by,
        )

    except raw_observations_service.InvalidRawObservationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except raw_observations_service.UnsupportedInputFormatError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )