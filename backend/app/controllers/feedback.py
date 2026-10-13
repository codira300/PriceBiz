from app.services import feedback as feedback_service


async def submit_feedback(
    *,
    observation_id: str,
    feedback_type: str,
):
    feedback = await feedback_service.submit_feedback(
        observation_id=observation_id,
        feedback_type=feedback_type,
    )

    return {
        "message": "Feedback recorded",
        "feedback": feedback,
    }