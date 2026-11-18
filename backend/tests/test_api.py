"""Integration tests for the AgriVision AI API."""
import os
import uuid
from io import BytesIO

os.environ.setdefault("DATABASE_URL", "sqlite:///./agrivision_test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-key-for-ci-which-is-long-enough-32-bytes")

from fastapi.testclient import TestClient
from PIL import Image
from app.main import app


def make_png():
    image = Image.new("RGB", (16, 16), color=(40, 150, 60))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def register_and_login(client):
    email = f"farmer-{uuid.uuid4().hex[:10]}@example.com"
    response = client.post("/api/v1/auth/register", json={
        "full_name": "Test Farmer",
        "email": email,
        "password": "SafeTestPassword123",
        "preferred_language": "en",
    })
    assert response.status_code == 201
    login = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "SafeTestPassword123",
    })
    assert login.status_code == 200
    return login.json()["access_token"]


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["project"] == "AgriVision AI"


def test_register_login_and_current_user():
    with TestClient(app) as client:
        token = register_and_login(client)
        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["role"] == "farmer"


def test_duplicate_registration_is_rejected():
    with TestClient(app) as client:
        email = f"duplicate-{uuid.uuid4().hex[:10]}@example.com"
        payload = {"full_name": "Test Farmer", "email": email, "password": "SafeTestPassword123"}
        assert client.post("/api/v1/auth/register", json=payload).status_code == 201
        assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_crop_case_requires_authentication():
    with TestClient(app) as client:
        response = client.post("/api/v1/cases", data={"crop_name": "Maize"}, files={"image": ("leaf.png", make_png(), "image/png")})
        assert response.status_code == 401


def test_farmer_can_submit_and_view_own_case():
    with TestClient(app) as client:
        token = register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/cases",
            headers=headers,
            data={"crop_name": "Maize", "location": "Gasabo", "description": "Leaf has unusual spots"},
            files={"image": ("leaf.png", make_png(), "image/png")},
        )
        assert response.status_code == 201
        case_id = response.json()["id"]
        assert response.json()["status"] == "submitted"
        history = client.get("/api/v1/cases/mine", headers=headers)
        assert history.status_code == 200
        assert any(case["id"] == case_id for case in history.json())


def test_crop_case_rejects_fake_image():
    with TestClient(app) as client:
        token = register_and_login(client)
        response = client.post(
            "/api/v1/cases",
            headers={"Authorization": f"Bearer {token}"},
            data={"crop_name": "Maize"},
            files={"image": ("fake.png", b"not really an image", "image/png")},
        )
        assert response.status_code == 415


def test_farmer_can_download_own_case_image():
    with TestClient(app) as client:
        token = register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}
        created = client.post(
            "/api/v1/cases",
            headers=headers,
            data={"crop_name": "Maize"},
            files={"image": ("leaf.png", make_png(), "image/png")},
        )
        assert created.status_code == 201
        image_response = client.get(f"/api/v1/cases/{created.json()['id']}/image", headers=headers)
        assert image_response.status_code == 200
        assert image_response.headers["content-type"] == "image/png"
