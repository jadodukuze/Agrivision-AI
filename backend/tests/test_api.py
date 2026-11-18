from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app import main
from app.main import app

client = TestClient(app)


def make_png() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (8, 8), color=(30, 150, 60)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["project"] == "AgriVision AI"
    assert response.json()["diagnosis_enabled"] is False


def test_crop_case_rejects_unsupported_file_type():
    response = client.post(
        "/api/v1/cases",
        data={"farmer_name": "Test Farmer", "crop_name": "Maize"},
        files={"image": ("note.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415


def test_crop_case_rejects_fake_image_content():
    response = client.post(
        "/api/v1/cases",
        data={"farmer_name": "Test Farmer", "crop_name": "Maize"},
        files={"image": ("fake.png", b"not really a png", "image/png")},
    )
    assert response.status_code == 400


def test_crop_case_accepts_valid_png_and_saves_it(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)
    response = client.post(
        "/api/v1/cases",
        data={
            "farmer_name": "Test Farmer",
            "crop_name": "Maize",
            "location": "Gasabo",
            "description": "Leaf has unusual spots.",
        },
        files={"image": ("leaf.png", make_png(), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "pending_expert_review"
    assert payload["diagnosis_enabled"] is False
    saved_files = list(tmp_path.iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].suffix == ".png"


def test_crop_case_rejects_file_over_size_limit():
    response = client.post(
        "/api/v1/cases",
        data={"farmer_name": "Test Farmer", "crop_name": "Maize"},
        files={"image": ("large.png", b"x" * (5 * 1024 * 1024 + 1), "image/png")},
    )
    assert response.status_code == 413
