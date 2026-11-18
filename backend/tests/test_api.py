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


def create_test_user(role: str):
    from app.database import SessionLocal
    from app.models import User
    from app.security import create_access_token, hash_password
    import uuid
    db = SessionLocal()
    try:
        email = f"{role}-{uuid.uuid4().hex[:12]}@example.com"
        user = User(full_name=f"Test {role.title()}", email=email, password_hash=hash_password("SafeTestPassword123"), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return create_access_token(str(user.id))
    finally:
        db.close()


def test_expert_can_review_farmer_case():
    with TestClient(app) as client:
        farmer_token = register_and_login(client)
        created = client.post(
            "/api/v1/cases",
            headers={"Authorization": f"Bearer {farmer_token}"},
            data={"crop_name": "Beans", "description": "Leaves look unusual"},
            files={"image": ("leaf.png", make_png(), "image/png")},
        )
        assert created.status_code == 201
        expert_token = create_test_user("expert")
        queue = client.get("/api/v1/expert/cases", headers={"Authorization": f"Bearer {expert_token}"})
        assert queue.status_code == 200
        case_id = created.json()["id"]
        assert any(item["id"] == case_id for item in queue.json())
        review = client.post(
            f"/api/v1/expert/cases/{case_id}/review",
            headers={"Authorization": f"Bearer {expert_token}"},
            json={"assessment": "The photo needs an in-person field inspection.", "recommended_next_steps": "Contact a local agricultural extension officer."},
        )
        assert review.status_code == 201
        details = client.get(f"/api/v1/cases/{case_id}", headers={"Authorization": f"Bearer {farmer_token}"})
        assert details.status_code == 200
        assert details.json()["reviews"][0]["assessment"].startswith("The photo")


def test_admin_can_create_expert_account():
    with TestClient(app) as client:
        admin_token = create_test_user("admin")
        response = client.post(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"full_name": "Agricultural Expert", "email": f"expert-{__import__('uuid').uuid4().hex[:8]}@example.com", "password": "ExpertAccountPass123", "role": "expert"},
        )
        assert response.status_code == 201
        assert response.json()["role"] == "expert"
