from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile

from backend.core.configs import Settings, settings
from starlette import status

CONTENT_TYPE_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/jpeg": ".jpeg",
    "image/png": ".png",
    "image/webp": ".webp"
}

MAX_IMAGE_SIZE = settings.max_image_size_mb * 1024 * 1024


def _validate_content_type(content_type: str | None) -> str:
    if content_type not in CONTENT_TYPE_TO_EXT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {content_type}. Allowed jpeg, png, webp",
        )
    return CONTENT_TYPE_TO_EXT[content_type]

async def save_upload(
        subdir: str,
        entity_id: UUID,
        file: UploadFile
):
    extension = _validate_content_type(file.content_type)

    contents = await file.read()

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Image exceeds {settings.max_image_size_mb} MB in size",
        )

    filename = f"{uuid4().hex}{extension}"
    relative_path = f"{subdir}/{entity_id}/{filename}"

    absolute_path = Path(settings.upload_root) / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_bytes(contents)

    return relative_path

def delete_file(relative_path: str) -> None:
    absolute_path = Path(settings.upload_root) / relative_path
    absolute_path.unlink(missing_ok=True)
