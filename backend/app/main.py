from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
ALLOWED_TYPES = {
    "image/jpeg": ("JPEG", ".jpg"),
    "image/png": ("PNG", ".png"),
    "image/webp": ("WEBP", ".webp"),
}

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "AGRI_ALLOWED_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500",
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="AgriVision AI",
    description="Crop-health case submission and expert-review platform.",
    version="0.3.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def validate_image(content: bytes, content_type: str) -> str:
    """Verify image bytes and ensure the actual format matches the declared MIME type."""
    expected = ALLOWED_TYPES.get(content_type)
    if expected is None:
        raise HTTPException(
            status_code=415,
            detail="Upload a JPG, PNG, or WebP image.",
        )
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")

    try:
        with Image.open(BytesIO(content)) as image:
            actual_format = image.format
            width, height = image.size
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        ) from None

    if actual_format != expected[0]:
        raise HTTPException(
            status_code=415,
            detail="The file contents do not match the selected image type.",
        )
    if width < 1 or height < 1 or width * height > MAX_IMAGE_PIXELS:
        raise HTTPException(
            status_code=413,
            detail="The image dimensions are not supported.",
        )
    return expected[1]


@app.get("/", tags=["General"])
def root():
    return {
        "project": "AgriVision AI",
        "status": "development",
        "docs": "/docs",
        "diagnosis_enabled": False,
    }


@app.get("/health", tags=["General"])
def health():
    return {"status": "ok"}


@app.post("/api/v1/cases", tags=["Crop cases"])
async def create_case(
    farmer_name: str = Form(..., min_length=2, max_length=100),
    crop_name: str = Form(..., min_length=2, max_length=80),
    location: str = Form("", max_length=120),
    description: str = Form("", max_length=1000),
    image: UploadFile = File(...),
):
    """Store a validated crop photo for future assessment; this endpoint does not diagnose disease."""
    content = await image.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Image must not exceed 5 MB.",
        )

    extension = validate_image(content, image.content_type or "")
    case_id = str(uuid4())
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / f"{case_id}{extension}").write_bytes(content)

    # Case metadata is not persisted yet. Authentication and database-backed case
    # storage are separate planned milestones; do not imply this is a full case record.
    return {
        "case_id": case_id,
        "status": "pending_expert_review",
        "diagnosis_enabled": False,
        "message": (
            "Photo received. Automated diagnosis is not enabled. "
            "An agricultural expert should review this case."
        ),
        "crop_name": crop_name,
        "location": location,
    }
