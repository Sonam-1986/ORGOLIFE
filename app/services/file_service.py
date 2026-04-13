"""
File service — abstracts save/retrieve for uploaded documents.
Uses local disk storage (cloud-ready: swap save logic for S3/GCS).
"""
import os
import uuid
import logging
from typing import Optional
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_MIME_MAP = {
    b"%PDF": "application/pdf",
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
}

MIME_TO_EXT = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
}


def _sniff_mime(header: bytes) -> str:
    """Detect MIME type from the first 4 bytes (magic bytes)."""
    for magic, mime in ALLOWED_MIME_MAP.items():
        if header.startswith(magic):
            return mime
    return "unknown"


async def save_upload(
    file: UploadFile,
    sub_folder: str,
    user_id: str,
    field_name: str,
) -> str:
    """
    Validate and persist an uploaded file to disk.
    Returns relative path stored in DB.
    Raises HTTPException on type/size violations.
    """
    content = await file.read()
    size = len(content)

    # ── Size guard ────────────────────────────────────────────────
    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{field_name}' file is empty."
        )
    if size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"'{field_name}': {size / 1048576:.2f} MB exceeds "
                f"the {settings.MAX_FILE_SIZE_MB} MB limit."
            )
        )

    # ── Magic byte MIME detection ─────────────────────────────────
    mime = _sniff_mime(content[:4])
    if mime == "unknown":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"'{field_name}': Unsupported file type. Allowed: PDF, JPG, PNG."
        )

    ext = MIME_TO_EXT[mime]
    uid = uuid.uuid4().hex[:10]
    filename = f"{user_id}_{field_name}_{uid}.{ext}"
    dir_path = os.path.join(settings.UPLOAD_DIR, sub_folder)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, filename)

    # ── Async write ───────────────────────────────────────────────
    async with aiofiles.open(file_path, "wb") as out:
        await out.write(content)

    logger.info(f"Saved file: {file_path} ({size} bytes, {mime})")
    return file_path


def file_url(path: Optional[str]) -> str:
    """Convert local path → URL path for API responses. Returns empty string if path is None."""
    if not path:
        return ""
    return "/" + path.replace("\\", "/")
