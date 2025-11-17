from fastapi.testclient import TestClient
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
SERVICE_ROOT = os.path.dirname(CURRENT_DIR)
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)

from app.main import app  # noqa: E402

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommendations_returns_products():
    payload = {
        "body_type": "rectangular",
        "face_shape": "ovalado",
        "color_palette": ["#ffffff", "#000000"],
        "style_hint": "urbano",
        "categories": [
            "camisa Oxford blanca",
            "vaqueros slim azul oscuro",
        ],
    }

    response = client.post("/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0

    first = data["items"][0]
    for key in ["name", "store", "category", "url"]:
        assert key in first
