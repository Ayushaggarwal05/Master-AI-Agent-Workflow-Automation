import os
import re
import time
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt", ".json", ".log"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024 # 50 MB limit

class UploadResponse(BaseModel):
    success: bool
    filename: str
    file_path: str
    size_bytes: int
    content_type: str
    message: str


@router.post(
    "",
    response_model=UploadResponse,
    summary="Upload Input Dataset File",
    description="Accepts CSV or XLSX files for workflow input processing, validates format, and saves to secure temporary storage."
)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename."
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Sanitize filename
    clean_name = re.sub(r"[^\w\.-]", "_", file.filename)
    timestamp = int(time.time())
    unique_filename = f"{timestamp}_{clean_name}"
    
    # Store in backend upload directory
    upload_dir = settings.BACKEND_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination_path = upload_dir / unique_filename

    try:
        size = 0
        with open(destination_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_FILE_SIZE_BYTES:
                    destination_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File size exceeds the 50MB maximum limit."
                    )
                buffer.write(chunk)
                
        logger.info(f"File uploaded successfully: {file.filename} -> {destination_path.resolve()} ({size} bytes)")
        
        return UploadResponse(
            success=True,
            filename=file.filename,
            file_path=str(destination_path.resolve()),
            size_bytes=size,
            content_type=file.content_type or "application/octet-stream",
            message=f"File '{file.filename}' uploaded and ready for workflow execution."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}", exc_info=True)
        destination_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store uploaded file: {str(e)}"
        )
