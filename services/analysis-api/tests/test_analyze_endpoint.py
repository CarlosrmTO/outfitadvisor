from fastapi.testclient import TestClient
import io
import os
import sys

# Aseguramos que la carpeta raíz del servicio esté en sys.path para poder importar app.main
CURRENT_DIR = os.path.dirname(__file__)
SERVICE_ROOT = os.path.dirname(CURRENT_DIR)
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)

from app.main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_requires_image_and_form_fields():
    # Enviamos solo el formulario sin imagen
    data = {"height": "170", "weight": "70"}
    response = client.post("/analyze", data=data)
    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower()


def test_analyze_ok_with_mock_image():
    # Creamos una imagen falsa en memoria
    fake_image_content = b"fake-image-bytes"
    files = {"photo": ("test.jpg", io.BytesIO(fake_image_content), "image/jpeg")}
    data = {"height": "170", "weight": "70"}

    response = client.post("/analyze", data=data, files=files)

    assert response.status_code == 200
    body = response.json()

    # Estructura mínima del resultado
    assert body["status"] == "success"
    analysis = body["analysis"]
    assert "body_type" in analysis
    assert "face_shape" in analysis
    assert "color_palette" in analysis
    assert "recommendations" in analysis
    assert isinstance(analysis["recommendations"], list)
