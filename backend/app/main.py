from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_BYTES = 5 * 1024 * 1024

app = FastAPI(title="AgriVision AI", description="Crop-health case submission and expert-review platform.", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])

@app.get("/", tags=["General"])
def root():
    return {"project": "AgriVision AI", "status": "development", "docs": "/docs"}

@app.get("/health", tags=["General"])
def health():
    return {"status": "ok"}

@app.post("/api/v1/cases", tags=["Crop cases"])
async def create_case(farmer_name: str = Form(..., min_length=2, max_length=100), crop_name: str = Form(..., min_length=2, max_length=80), location: str = Form("", max_length=120), description: str = Form("", max_length=1000), image: UploadFile = File(...)):
    """Save a photo for future assessment. This endpoint does not diagnose disease."""
    extension = ALLOWED_TYPES.get(image.content_type or "")
    if not extension:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG, or WebP image.")
    content = await image.read(MAX_BYTES + 1)
    if not content or len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image must be between 1 byte and 5 MB.")
    case_id = str(uuid4())
    (UPLOAD_DIR / f"{case_id}{extension}").write_bytes(content)
    return {"case_id": case_id, "status": "pending_expert_review", "message": "Photo received. AI diagnosis is not enabled yet; an agricultural expert should review this case.", "farmer_name": farmer_name, "crop_name": crop_name, "location": location, "description": description}
