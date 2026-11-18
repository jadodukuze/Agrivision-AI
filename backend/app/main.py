import os
import hmac
from pathlib import Path
from uuid import uuid4
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import User, CropCase, ExpertReview
from .security import create_access_token, decode_access_token, hash_password, verify_password

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "storage" / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
ALLOWED_TYPES = {"image/jpeg": ("JPEG", ".jpg"), "image/png": ("PNG", ".png"), "image/webp": ("WEBP", ".webp")}
security = HTTPBearer(auto_error=False)

app = FastAPI(title="AgriVision AI", description="Crop-health case management and expert-review platform. AI diagnosis is not enabled.", version="0.4.0")
origins = [item.strip() for item in os.getenv("CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["GET", "POST", "PATCH"], allow_headers=["Authorization", "Content-Type"])

@app.on_event("startup")
def create_tables():
    # In production, apply versioned Alembic migrations before starting the API.
    if os.getenv("APP_ENV", "development").lower() == "development":
        Base.metadata.create_all(bind=engine)

class RegisterInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=190)
    password: str = Field(min_length=10, max_length=128)
    preferred_language: str = Field(default="en", pattern="^(en|rw)$")

class LoginInput(BaseModel):
    email: str
    password: str

class StaffInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=190)
    password: str = Field(min_length=10, max_length=128)
    role: str = Field(pattern="^(expert|admin)$")

class BootstrapAdminInput(BaseModel):
    email: str = Field(min_length=5, max_length=190)
    setup_token: str = Field(min_length=32, max_length=256)

class ReviewInput(BaseModel):
    assessment: str = Field(min_length=5, max_length=5000)
    recommended_next_steps: Optional[str] = Field(default=None, max_length=3000)

def user_view(user: User):
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role, "preferred_language": user.preferred_language}

def case_view(case: CropCase):
    return {"id": case.id, "farmer_id": case.farmer_id, "farmer_name": case.farmer.full_name, "crop_name": case.crop_name, "location": case.location, "description": case.description, "status": case.status, "created_at": case.created_at.isoformat(), "reviews": [{"assessment": r.assessment, "recommended_next_steps": r.recommended_next_steps, "reviewed_at": r.reviewed_at.isoformat()} for r in case.reviews]}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload.get("sub", ""))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User account is unavailable.")
    return user

def require_roles(*roles):
    def dependency(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
        return user
    return dependency

@app.get("/", tags=["General"])
def root():
    return FileResponse(BASE_DIR.parent / "frontend" / "index.html")

@app.get("/health", tags=["General"])
def health():
    return {"status": "ok"}

@app.post("/api/v1/auth/register", status_code=201, tags=["Authentication"])
def register(data: RegisterInput, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(full_name=data.full_name.strip(), email=email, password_hash=hash_password(data.password), role="farmer", preferred_language=data.preferred_language)
    db.add(user); db.commit(); db.refresh(user)
    return user_view(user)

@app.post("/api/v1/auth/login", tags=["Authentication"])
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.strip().lower()).first()
    if user is None or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return {"access_token": create_access_token(user.id, user.role), "token_type": "bearer", "user": user_view(user)}

@app.get("/api/v1/auth/me", tags=["Authentication"])
def me(user: User = Depends(get_current_user)):
    return user_view(user)

@app.post("/api/v1/admin/bootstrap", tags=["Administration"])
def bootstrap_first_admin(data: BootstrapAdminInput, db: Session = Depends(get_db)):
    """Promote the one configured account only once, using a private Render secret."""
    configured_email = os.getenv("ADMIN_BOOTSTRAP_EMAIL", "").strip().lower()
    configured_token = os.getenv("ADMIN_BOOTSTRAP_TOKEN", "")
    if not configured_email or len(configured_token) < 32:
        raise HTTPException(status_code=503, detail="First-admin setup is not enabled.")
    if not hmac.compare_digest(data.setup_token, configured_token):
        raise HTTPException(status_code=403, detail="Invalid setup credentials.")
    if not hmac.compare_digest(data.email.strip().lower(), configured_email):
        raise HTTPException(status_code=403, detail="This account is not authorized for first-admin setup.")

    # Lock the designated account so simultaneous setup requests cannot both pass.
    user = db.query(User).filter(User.email == configured_email).with_for_update().first()
    if user is None:
        raise HTTPException(status_code=404, detail="The configured account must register before setup.")
    if db.query(User).filter(User.role == "admin").first() is not None:
        raise HTTPException(status_code=409, detail="An administrator is already configured.")
    user.role = "admin"
    db.commit()
    db.refresh(user)
    return {"message": "First administrator configured. Remove ADMIN_BOOTSTRAP_TOKEN from Render now, then sign in again.", "user": user_view(user)}

@app.post("/api/v1/admin/users", status_code=201, tags=["Administration"])
def create_staff(data: StaffInput, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    email = data.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(full_name=data.full_name.strip(), email=email, password_hash=hash_password(data.password), role=data.role)
    db.add(user); db.commit(); db.refresh(user)
    return user_view(user)

@app.get("/api/v1/admin/summary", tags=["Administration"])
def admin_summary(db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return {"users": db.query(User).count(), "farmers": db.query(User).filter(User.role == "farmer").count(), "experts": db.query(User).filter(User.role == "expert").count(), "cases": db.query(CropCase).count(), "pending_cases": db.query(CropCase).filter(CropCase.status.in_(["submitted", "under_review"])).count()}

@app.post("/api/v1/cases", status_code=201, tags=["Crop cases"])
async def create_case(crop_name: str = Form(..., min_length=2, max_length=80), location: str = Form("", max_length=120), description: str = Form("", max_length=1000), image: UploadFile = File(...), db: Session = Depends(get_db), farmer: User = Depends(require_roles("farmer"))):
    expected = ALLOWED_TYPES.get(image.content_type or "")
    if expected is None:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG, or WebP image.")
    content = await image.read(MAX_BYTES + 1)
    if not content or len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image must be between 1 byte and 5 MB.")
    try:
        from io import BytesIO
        with Image.open(BytesIO(content)) as picture:
            actual, width, height = picture.format, picture.width, picture.height
            picture.verify()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(status_code=415, detail="The uploaded file is not a valid image.")
    if actual != expected[0]:
        raise HTTPException(status_code=415, detail="The file contents do not match the selected image type.")
    if width < 1 or height < 1 or width * height > MAX_IMAGE_PIXELS:
        raise HTTPException(status_code=413, detail="The image dimensions are not supported.")
    filename = f"{uuid4().hex}{expected[1]}"
    destination = UPLOAD_DIR / filename
    destination.write_bytes(content)
    case = CropCase(farmer_id=farmer.id, crop_name=crop_name.strip(), location=location.strip() or None, description=description.strip() or None, image_path=filename, status="submitted")
    db.add(case); db.commit(); db.refresh(case)
    return {"id": case.id, "status": case.status, "message": "Photo received. It is awaiting expert review; AI diagnosis is not enabled."}

@app.get("/api/v1/cases/mine", tags=["Crop cases"])
def my_cases(db: Session = Depends(get_db), farmer: User = Depends(require_roles("farmer"))):
    cases = db.query(CropCase).filter(CropCase.farmer_id == farmer.id).order_by(CropCase.created_at.desc()).all()
    return [case_view(case) for case in cases]

@app.get("/api/v1/expert/cases", tags=["Expert review"])
def expert_cases(db: Session = Depends(get_db), expert: User = Depends(require_roles("expert", "admin"))):
    cases = db.query(CropCase).order_by(CropCase.created_at.desc()).all()
    return [case_view(case) for case in cases]

@app.get("/api/v1/expert/cases/{case_id}/image", tags=["Expert review"])
def expert_case_image(
    case_id: int,
    db: Session = Depends(get_db),
    expert: User = Depends(require_roles("expert", "admin")),
):
    """Return a submitted image only to authenticated expert or admin accounts."""
    case = db.query(CropCase).filter(CropCase.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail="Crop case not found.")

    stored_name = case.image_path
    if not stored_name or Path(stored_name).name != stored_name:
        raise HTTPException(status_code=404, detail="Crop image not found.")

    upload_root = UPLOAD_DIR.resolve()
    image_path = (upload_root / stored_name).resolve()
    if image_path.parent != upload_root or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Crop image not found.")

    media_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(image_path.suffix.lower(), "application/octet-stream")
    return FileResponse(image_path, media_type=media_type, filename=image_path.name)
@app.post("/api/v1/expert/cases/{case_id}/review", tags=["Expert review"])
def review_case(case_id: int, data: ReviewInput, db: Session = Depends(get_db), expert: User = Depends(require_roles("expert", "admin"))):
    case = db.query(CropCase).filter(CropCase.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail="Crop case not found.")
    review = ExpertReview(case_id=case.id, expert_id=expert.id, assessment=data.assessment.strip(), recommended_next_steps=(data.recommended_next_steps or "").strip() or None)
    case.status = "reviewed"
    db.add(review); db.commit(); db.refresh(case)
    return case_view(case)


FRONTEND_DIR = BASE_DIR.parent / "frontend"
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="frontend-css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="frontend-js")
