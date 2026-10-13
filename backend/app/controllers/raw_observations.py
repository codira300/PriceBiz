from typing import Optional

from app.services import raw_observations as raw_observations_service


async def create_raw_observation(
    *,
    input_format: str,
    payload: dict,
    source_id: Optional[str] = None,
):
    return await raw_observations_service.create_raw_observation(
        input_format=input_format,
        payload=payload,
        source_id=source_id,
    )


async def find_raw_observations(
    *,
    input_format: Optional[str] = None,
    processing_status: Optional[str] = None,
    source_id: Optional[str] = None,
):
    return await raw_observations_service.find_raw_observations(
        input_format=input_format,
        processing_status=processing_status,
        source_id=source_id,
    )


async def get_raw_observation(
    *,
    observation_id: str,
):
    return await raw_observations_service.get_raw_observation(
        observation_id=observation_id,
    )


async def update_processing_status(
    *,
    observation_id: str,
    processing_status: str,
):
    return await raw_observations_service.update_processing_status(
        observation_id=observation_id,
        processing_status=processing_status,
    )


async def process_raw_observation(
    *,
    observation_id: str,
    creator_id: Optional[str] = None,
    submitted_by: Optional[str] = None,
):
    return await raw_observations_service.process_raw_observation(
        observation_id=observation_id,
        creator_id=creator_id,
        submitted_by=submitted_by,
    )


async def process_pending_raw_observations(
    *,
    input_format: Optional[str] = None,
    creator_id: Optional[str] = None,
    submitted_by: Optional[str] = None,
):
    return await raw_observations_service.process_pending_raw_observations(
        input_format=input_format,
        creator_id=creator_id,
        submitted_by=submitted_by,
    )
    
async def queue_process_pending_raw_observations(
    *,
    input_format=None,
    creator_id=None,
    submitted_by=None,
):
    return await raw_observations_service.queue_process_pending_raw_observations(
        input_format=input_format,
        creator_id=creator_id,
        submitted_by=submitted_by,
    )