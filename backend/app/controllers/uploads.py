from app.services import uploads as uploads_service


async def upload_image(
    *,
    content_type: str | None,
    contents: bytes,
):
    return await uploads_service.upload_image(
        content_type=content_type,
        contents=contents,
    )