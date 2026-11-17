from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["project"] == "AgriVision AI"

def test_crop_case_rejects_unsupported_file_type():
    response = client.post(
        "/api/v1/cases",
        data={"farmer_name": "Test Farmer", "crop_name": "Maize"},
        files={"image": ("note.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415
