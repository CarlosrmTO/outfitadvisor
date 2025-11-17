from fastapi.testclient import TestClient
from unittest.mock import patch
import io
import os
import sys

# Aseguramos que la carpeta raíz del servicio esté en sys.path para poder importar app.main
CURRENT_DIR = os.path.dirname(__file__)
SERVICE_ROOT = os.path.dirname(CURRENT_DIR)
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)

from app.main import app
from app.models import AnalysisResult

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


@patch("app.main.analyze_with_openai")
def test_analyze_ok_with_mock_image(mock_analyze):
    # Mock de la respuesta de OpenAI para que los tests no dependan del servicio externo
    mock_analyze.return_value = AnalysisResult(
        body_type="rectangular",
        face_shape="oval",
        color_palette=["#111111", "#222222"],
        recommendations=["Prenda 1", "Prenda 2"],
    )

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
    assert analysis["body_type"] == "rectangular"
    assert analysis["face_shape"] == "oval"
    assert analysis["color_palette"] == ["#111111", "#222222"]
    assert analysis["recommendations"] == ["Prenda 1", "Prenda 2"]
