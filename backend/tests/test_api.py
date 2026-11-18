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
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db

def register_and_login(client):
    payload = {"full_name": "Test Farmer", "email": "farmer@example.com", "password": "StrongTestPass123", "preferred_language": "en"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200
    return login.json()["access_token"]

def png_bytes():
    image = Image.new("RGB", (16, 16), "green")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()

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
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["role"] == "farmer"

def test_duplicate_email_is_rejected(client):
    register_and_login(client)
    response = client.post("/api/v1/auth/register", json={"full_name":"Another Farmer","email":"farmer@example.com","password":"StrongTestPass123"})
    assert response.status_code == 409

def test_cases_require_authentication(client):
    response = client.get("/api/v1/cases/mine")
    assert response.status_code == 401

def test_farmer_can_submit_and_view_case(client, monkeypatch, tmp_path):
    import app.main as main
    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)
    token = register_and_login(client)
    response = client.post("/api/v1/cases", headers={"Authorization": f"Bearer {token}"}, data={"crop_name":"Maize","location":"Gasabo","description":"Leaf spots"}, files={"image":("leaf.png",png_bytes(),"image/png")})
    assert response.status_code == 201
    assert response.json()["status"] == "submitted"
    cases = client.get("/api/v1/cases/mine", headers={"Authorization": f"Bearer {token}"})
    assert cases.status_code == 200
    assert len(cases.json()) == 1
    assert cases.json()[0]["crop_name"] == "Maize"

def test_upload_rejects_invalid_image_content(client):
    token = register_and_login(client)
    response = client.post("/api/v1/cases", headers={"Authorization": f"Bearer {token}"}, data={"crop_name":"Maize"}, files={"image":("fake.png",b"not an image","image/png")})
    assert response.status_code == 415

def test_farmer_cannot_access_expert_queue(client):
    token = register_and_login(client)
    response = client.get("/api/v1/expert/cases", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
