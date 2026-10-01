import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ms-ia-summary"


def test_summarize_exitoso(mocker):
    mocker.patch(
        "service.summary_service.generar_resumen",
        return_value="Este es un resumen de prueba generado por el mock."
    )

    response = client.post(
        "/summarize",
        json={"text": "Este es un texto largo de ejemplo para que la IA lo resuma correctamente."}
    )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["summary"]) > 0


def test_summarize_texto_vacio():
    response = client.post(
        "/summarize",
        json={"text": ""}
    )
    assert response.status_code == 400


def test_summarize_texto_corto():
    response = client.post(
        "/summarize",
        json={"text": "Hola"}
    )
    assert response.status_code == 400