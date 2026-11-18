"""AgriVision AI API: authenticated crop cases and expert review."""
import os
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session
import jwt

from .database import Base, engine, get_db
from .models import CropCase, ExpertReview, User
from .schemas import CaseResponse, LoginRequest, RegisterRequest, ReviewRequest, TokenResponse, UserResponse, StaffCreateRequest
from .security import create_access_token, decode_access_token, hash_password, verify_password

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "storage" / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_BYTES = 5 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


origins = [value.strip() for value in os.getenv("CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500").split(",") if value.strip()]


def initialize_database():
    Base.metadata.create_all(bind=engine)
    # Optional first administrator. Set both values as deployment secrets.
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if admin_email and admin_password:
        db = next(get_db())
        try:
            existing = db.scalar(select(User).where(User.email == admin_email.lower()))
            if not existing:
                db.add(User(
                    full_name=os.getenv("ADMIN_FULL_NAME", "AgriVision Administrator"),
                    email=admin_email.lower(),
                    password_hash=hash_password(admin_password),
                    role="admin",
                ))
                db.commit()
        finally:
            db.close()


@asynccontextmanager
async def lifespan(application: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="AgriVision AI",
    description="Crop-health case submission and agricultural expert review. AI diagnosis is not enabled.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/", tags=["General"])
def root():
    return {"project": "AgriVision AI", "status": "development", "api_version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["General"])
def health(db: Session = Depends(get_db)):
    try:
        db.execute(select(1))
        return {"status": "ok", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    unauthorized = HTTPException(status_code=401, detail="Invalid or expired access token", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub", ""))
    except (jwt.PyJWTError, TypeError, ValueError):
        raise unauthorized
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise unauthorized
    return user


def require_roles(*roles: str):
    def checker(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
        return user
    return checker


@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=201, tags=["Authentication"])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role="farmer",
        preferred_language=payload.preferred_language,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_access_token(str(user.id)), "user": user}


@app.get("/api/v1/auth/me", response_model=UserResponse, tags=["Authentication"])
def read_me(user: User = Depends(current_user)):
    return user


@app.get("/api/v1/crops", tags=["Crop information"])
def list_supported_crops():
    return {"crops": ["Maize", "Beans", "Irish potato", "Tomato", "Cassava", "Banana", "Rice", "Wheat", "Other"]}


@app.post("/api/v1/cases", response_model=CaseResponse, status_code=201, tags=["Crop cases"])
async def create_case(
    crop_name: str = Form(..., min_length=2, max_length=80),
    location: str = Form("", max_length=120),
    description: str = Form("", max_length=1000),
    image: UploadFile = File(...),
    user: User = Depends(require_roles("farmer", "admin")),
    db: Session = Depends(get_db),
):
    """Create a private crop-health case. No automated disease diagnosis is performed."""
    content = await image.read(MAX_BYTES + 1)
    if not content or len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image must be between 1 byte and 5 MB")
    try:
        from io import BytesIO
        with Image.open(BytesIO(content)) as picture:
            image_format = picture.format
            picture.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(status_code=415, detail="The uploaded file is not a valid supported image")
    extension = ALLOWED_FORMATS.get(image_format)
    if not extension:
        raise HTTPException(status_code=415, detail="Upload a valid JPG, PNG, or WebP image")
    case_id = str(uuid4())
    destination = UPLOAD_DIR / f"{case_id}{extension}"
    destination.write_bytes(content)
    case = CropCase(
        id=case_id,
        farmer_id=user.id,
        crop_name=crop_name.strip(),
        location=location.strip() or None,
        description=description.strip() or None,
        image_path=str(destination),
        status="submitted",
    )
    try:
        db.add(case)
        db.commit()
        db.refresh(case)
    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise
    return CaseResponse(
        id=case.id, farmer_id=case.farmer_id, crop_name=case.crop_name,
        location=case.location, description=case.description,
        status=case.status, created_at=case.created_at, has_image=True,
    )


@app.get("/api/v1/cases/mine", response_model=list[CaseResponse], tags=["Crop cases"])
def my_cases(user: User = Depends(require_roles("farmer", "admin")), db: Session = Depends(get_db)):
    cases = db.scalars(select(CropCase).where(CropCase.farmer_id == user.id).order_by(CropCase.created_at.desc())).all()
    return [CaseResponse(id=c.id, farmer_id=c.farmer_id, crop_name=c.crop_name, location=c.location, description=c.description, status=c.status, created_at=c.created_at) for c in cases]


@app.get("/api/v1/expert/cases", tags=["Expert review"])
def expert_case_queue(user: User = Depends(require_roles("expert", "admin")), db: Session = Depends(get_db)):
    cases = db.scalars(select(CropCase).order_by(CropCase.created_at.asc())).all()
    return [{"id": c.id, "farmer_id": c.farmer_id, "farmer_name": c.farmer.full_name, "crop_name": c.crop_name, "location": c.location, "description": c.description, "status": c.status, "created_at": c.created_at, "has_image": bool(c.image_path)} for c in cases]


@app.post("/api/v1/expert/cases/{case_id}/review", status_code=201, tags=["Expert review"])
def review_case(case_id: str, payload: ReviewRequest, user: User = Depends(require_roles("expert", "admin")), db: Session = Depends(get_db)):
    case = db.get(CropCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Crop case not found")
    review = ExpertReview(
        case_id=case.id,
        expert_id=user.id,
        assessment=payload.assessment.strip(),
        recommended_next_steps=(payload.recommended_next_steps or "").strip() or None,
    )
    case.status = "reviewed"
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"review_id": review.id, "case_id": case.id, "status": case.status, "message": "Expert review saved"}


@app.get("/api/v1/cases/{case_id}", tags=["Crop cases"])
def get_case(case_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    case = db.get(CropCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Crop case not found")
    if user.role == "farmer" and case.farmer_id != user.id:
        raise HTTPException(status_code=404, detail="Crop case not found")
    reviews = []
    if user.role in {"expert", "admin"} or case.farmer_id == user.id:
        reviews = [{"assessment": r.assessment, "recommended_next_steps": r.recommended_next_steps, "reviewed_at": r.reviewed_at} for r in case.reviews]
    return {"id": case.id, "crop_name": case.crop_name, "location": case.location, "description": case.description, "status": case.status, "created_at": case.created_at, "reviews": reviews, "ai_prediction": None, "ai_status": "not_available"}


@app.get("/api/v1/admin/users", response_model=list[UserResponse], tags=["Administration"])
def admin_users(user: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.created_at.desc())).all()


@app.post("/api/v1/admin/users/{user_id}/deactivate", tags=["Administration"])
def deactivate_user(user_id: int, user: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")
    target.is_active = False
    db.commit()
    return {"message": "User account deactivated", "user_id": target.id}


@app.post("/api/v1/admin/users", response_model=UserResponse, status_code=201, tags=["Administration"])
def create_staff_account(payload: StaffCreateRequest, admin: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    """Create an expert or administrator account; public registration cannot grant privileged roles."""
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(full_name=payload.full_name.strip(), email=email, password_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/api/v1/admin/summary", tags=["Administration"])
def admin_summary(admin: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    from sqlalchemy import func
    count = lambda statement: db.scalar(statement) or 0
    return {
        "users": count(select(func.count()).select_from(User)),
        "farmers": count(select(func.count()).select_from(User).where(User.role == "farmer")),
        "experts": count(select(func.count()).select_from(User).where(User.role == "expert")),
        "cases": count(select(func.count()).select_from(CropCase)),
        "pending_cases": count(select(func.count()).select_from(CropCase).where(CropCase.status.in_(["submitted", "under_review"]))),
    }


@app.get("/api/v1/cases/{case_id}/image", tags=["Crop cases"])
def get_case_image(case_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Return a case photo only to its owner or an authorised expert/admin."""
    case = db.get(CropCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Crop case not found")
    if user.role == "farmer" and case.farmer_id != user.id:
        raise HTTPException(status_code=404, detail="Crop case not found")
    image_path = Path(case.image_path).resolve()
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Crop image is unavailable")
    media_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    media_type = media_types.get(image_path.suffix.lower())
    if not media_type:
        raise HTTPException(status_code=415, detail="Unsupported stored image type")
    return FileResponse(image_path, media_type=media_type, filename=image_path.name)
