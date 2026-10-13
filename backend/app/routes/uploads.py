from fastapi import APIRouter, File, HTTPException, UploadFile

from app.controllers import uploads as uploads_controller
from app.services import uploads as uploads_service


router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
):
    contents = await file.read()

    try:
        return await uploads_controller.upload_image(
            content_type=file.content_type,
            contents=contents,
        )

    except uploads_service.InvalidImageTypeError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except uploads_service.ImageTooLargeError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )