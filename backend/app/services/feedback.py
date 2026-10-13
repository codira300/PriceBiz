from app.database import price_observations as price_observations_db


VALID_FEEDBACK_TYPES = {
    "useful",
    "not_useful",
    "reports",
}


class FeedbackError(Exception):
    pass


class InvalidFeedbackTypeError(FeedbackError):
    pass


class PriceObservationNotFoundError(FeedbackError):
    pass


class FeedbackRecordingError(FeedbackError):
    pass


async def submit_feedback(
    observation_id: str,
    feedback_type: str,
):
    if feedback_type not in VALID_FEEDBACK_TYPES:
        raise InvalidFeedbackTypeError(
            "Invalid feedback type"
        )

    observation = await (
        price_observations_db.increment_feedback(
            observation_id=observation_id,
            feedback_type=feedback_type,
        )
    )

    if observation is None:
        raise PriceObservationNotFoundError(
            "Price observation not found"
        )

    return observation["feedback"]