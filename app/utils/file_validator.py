"""
File validation: type checking, size limits, and safe filename generation.
Uses magic-byte sniffing (no external python-magic dependency).
"""
import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

# Magic bytes → MIME type mapping
_MAGIC_MIME: dict = {
    b"%PDF": "application/pdf",
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
}

# MIME type → file extension
ALLOWED_MIME_TYPES: dict = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
}


def _sniff_mime(header: bytes) -> str:
    """Detect MIME type from the first 4 bytes (magic bytes)."""
    for magic, mime in _MAGIC_MIME.items():
        if header.startswith(magic):
            return mime
    return "unknown"


async def validate_and_save_file(
    file: UploadFile,
    sub_folder: str,
    user_id: str,
    field_name: str,
) -> str:
    """
    Validate file type & size via magic bytes, then save asynchronously.
    Returns the relative file path for DB storage.
    Raises HTTPException on validation failure.
    """
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name}: File is empty.",
        )
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"{field_name}: {file_size / 1048576:.2f} MB exceeds "
                f"the {settings.MAX_FILE_SIZE_MB} MB limit."
            ),
        )

    mime_type = _sniff_mime(content[:4])
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"{field_name}: Unsupported file type. Allowed: PDF, JPG, PNG.",
        )

    ext = ALLOWED_MIME_TYPES[mime_type]
    safe_filename = f"{user_id}_{field_name}_{uuid.uuid4().hex[:8]}.{ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, sub_folder)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, safe_filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return file_path


def get_file_url(file_path: str) -> str:
    """Convert a local file path to a relative URL for the API response."""
    return "/" + file_path.replace("\\", "/")
