from fastapi import APIRouter, HTTPException

from app.controllers import feedback as feedback_controller
from app.services import feedback as feedback_service


router = APIRouter(
    prefix="/price-observations",
    tags=["Feedback"],
)


@router.post("/{observation_id}/feedback")
async def submit_feedback(
    observation_id: str,
    feedback_type: str,
):
    try:
        return await feedback_controller.submit_feedback(
            observation_id=observation_id,
            feedback_type=feedback_type,
        )

    except feedback_service.InvalidFeedbackTypeError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except feedback_service.PriceObservationNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except feedback_service.FeedbackRecordingError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )