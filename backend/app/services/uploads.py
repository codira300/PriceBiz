from pathlib import Path
from uuid import uuid4


UPLOAD_DIR = Path("uploads")

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


class UploadError(Exception):
    pass


class InvalidImageTypeError(UploadError):
    pass


class ImageTooLargeError(UploadError):
    pass


async def upload_image(
    *,
    content_type: str | None,
    contents: bytes,
):
    if content_type not in ALLOWED_TYPES:
        raise InvalidImageTypeError(
            "Only JPEG, PNG, and WebP images are allowed"
        )

    if len(contents) > MAX_IMAGE_SIZE:
        raise ImageTooLargeError(
            "Image must be smaller than 5MB"
        )

    UPLOAD_DIR.mkdir(exist_ok=True)

    extension = ALLOWED_TYPES[content_type]
    filename = f"{uuid4().hex}{extension}"

    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(contents)

    return {
        "filename": filename,
        "url": f"/uploads/{filename}",
    }