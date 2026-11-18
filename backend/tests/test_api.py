from io import BytesIO
import os

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["JWT_SECRET_KEY"] = "test-only-secret-key-not-for-production"

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import create_access_token, hash_password

test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as test_client:
        yield test_client

def png_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (16, 16), "green").save(output, format="PNG")
    return output.getvalue()

def register_and_login(client):
    details = {"full_name": "Test Farmer", "email": "farmer@example.com", "password": "StrongTestPass123", "preferred_language": "en"}
    registered = client.post("/api/v1/auth/register", json=details)
    assert registered.status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": details["email"], "password": details["password"]})
    assert login.status_code == 200
    return login.json()["access_token"]

def auth(token: str):
    return {"Authorization": f"Bearer {token}"}

def create_expert():
    db = TestingSessionLocal()
    try:
        expert = User(full_name="Test Expert", email="expert@example.com", password_hash=hash_password("StrongExpertPass123"), role="expert")
        db.add(expert)
        db.commit()
        db.refresh(expert)
        return expert.id
    finally:
        db.close()

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_discloses_ai_is_not_enabled(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["ai_diagnosis_enabled"] is False

def test_register_login_and_profile(client):
    token = register_and_login(client)
    response = client.get("/api/v1/auth/me", headers=auth(token))
    assert response.status_code == 200
    assert response.json()["role"] == "farmer"

def test_duplicate_email_is_rejected(client):
    register_and_login(client)
    response = client.post("/api/v1/auth/register", json={"full_name": "Another Farmer", "email": "FARMER@example.com", "password": "StrongTestPass123"})
    assert response.status_code == 409

def test_cases_require_authentication(client):
    response = client.get("/api/v1/cases/mine")
    assert response.status_code == 401

def test_farmer_can_submit_and_view_case(client, monkeypatch, tmp_path):
    import app.main as main
    monkeypatch.setattr(main, 'UPLOAD_DIR', tmp_path)
    token = register_and_login(client)
    response = client.post("/api/v1/cases", headers=auth(token), data={"crop_name": "Maize", "location": "Gasabo", "description": "Leaf spots"}, files={"image": ("leaf.png", png_bytes(), "image/png")})
    assert response.status_code == 201
    assert response.json()["status"] == "submitted"
    assert "AI diagnosis is not enabled" in response.json()["message"]
    cases = client.get("/api/v1/cases/mine", headers=auth(token))
    assert cases.status_code == 200
    assert len(cases.json()) == 1
    assert cases.json()[0]["crop_name"] == "Maize"

def test_upload_rejects_unsupported_type(client):
    token = register_and_login(client)
    response = client.post("/api/v1/cases", headers=auth(token), data={"crop_name": "Maize"}, files={"image": ("note.txt", b"not an image", "text/plain")})
    assert response.status_code == 415

def test_upload_rejects_invalid_image_content(client):
    token = register_and_login(client)
    response = client.post("/api/v1/cases", headers=auth(token), data={"crop_name": "Maize"}, files={"image": ("fake.png", b"not an image", "image/png")})
    assert response.status_code == 415

def test_upload_rejects_file_over_size_limit(client):
    token = register_and_login(client)
    response = client.post("/api/v1/cases", headers=auth(token), data={"crop_name": "Maize"}, files={"image": ("large.png", b"x" * (5 * 1024 * 1024 + 1), "image/png")})
    assert response.status_code == 413

def test_farmer_cannot_access_expert_queue_or_images(client):
    token = register_and_login(client)
    queue = client.get("/api/v1/expert/cases", headers=auth(token))
    image = client.get("/api/v1/expert/cases/1/image", headers=auth(token))
    assert queue.status_code == 403
    assert image.status_code == 403

def test_expert_can_access_uploaded_image_and_review_case(client, monkeypatch, tmp_path):
    import app.main as main
    monkeypatch.setattr(main, 'UPLOAD_DIR', tmp_path)
    farmer_token = register_and_login(client)
    created = client.post("/api/v1/cases", headers=auth(farmer_token), data={"crop_name": "Beans", "description": "Leaf spots"}, files={"image": ("beans.png", png_bytes(), "image/png")})
    assert created.status_code == 201
    case_id = created.json()["id"]
    expert_id = create_expert()
    expert_token = create_access_token(expert_id, "expert")
    image = client.get(f"/api/v1/expert/cases/{case_id}/image", headers=auth(expert_token))
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"
    assert image.content == png_bytes()
    reviewed = client.post(f"/api/v1/expert/cases/{case_id}/review", headers=auth(expert_token), json={"assessment": "The image needs an in-person field assessment.", "recommended_next_steps": "Contact a local agricultural extension officer."})
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "reviewed"
    assert len(reviewed.json()['reviews']) == 1

def test_admin_can_create_staff_and_view_summary(client):
    import uuid
    db = TestingSessionLocal()
    try:
        admin = User(
            full_name="Test Administrator",
            email=f"admin-{uuid.uuid4().hex[:10]}@example.com",
            password_hash=hash_password("StrongAdminPass123"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        admin_token = create_access_token(admin.id, admin.role)
    finally:
        db.close()

    created = client.post(
        "/api/v1/admin/users",
        headers=auth(admin_token),
        json={
            "full_name": "New Agricultural Expert",
            "email": f"new-expert-{uuid.uuid4().hex[:10]}@example.com",
            "password": "StrongExpertPass123",
            "role": "expert",
        },
    )
    assert created.status_code == 201
    assert created.json()["role"] == "expert"

    summary = client.get("/api/v1/admin/summary", headers=auth(admin_token))
    assert summary.status_code == 200
    assert summary.json()["experts"] >= 1


def test_farmer_cannot_create_staff_account(client):
    farmer_token = register_and_login(client)
    response = client.post(
        "/api/v1/admin/users",
        headers=auth(farmer_token),
        json={
            "full_name": "Not An Admin",
            "email": "not-admin@example.com",
            "password": "StrongPassword123",
            "role": "admin",
        },
    )
    assert response.status_code == 403
