import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Health check mejorado debe incluir version, uptime y timestamp."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ms-ia-summary"
    assert "version" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data


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


# ===== Tests de Nuevos Patrones de Resiliencia (Issue #5) =====

def test_rate_limit_devuelve_429(mocker):
    """Verifica que el patrón Rate Limit responde 429 si el semáforo está bloqueado."""
    mocker.patch("app.routers._summary_semaphore.locked", return_value=True)

    response = client.post(
        "/summarize",
        json={"text": "Este es un texto suficientemente largo para pasar la validacion inicial."}
    )
    assert response.status_code == 429
    assert "Demasiadas solicitudes" in response.json()["detail"]


def test_cache_resumen_hit(mocker):
    """Verifica que el patrón Cache devuelva el resumen almacenado sin volver a consultar."""
    from service import summary_service

    texto_prueba = "Texto de prueba para verificar el cache de resúmenes de IA."
    mock_generar = mocker.patch(
        "service.summary_service.cliente_ia.generate",
        return_value={"response": "Resumen cacheado exitosamente"}
    )

    # 1. Primera llamada (Cache MISS): debe llamar a generate
    res1 = summary_service.generar_resumen(texto_prueba)
    assert res1 == "Resumen cacheado exitosamente"
    assert mock_generar.call_count == 1

    # 2. Segunda llamada con el mismo texto (Cache HIT): NO debe llamar de nuevo a generate
    res2 = summary_service.generar_resumen(texto_prueba)
    assert res2 == "Resumen cacheado exitosamente"
    assert mock_generar.call_count == 1  # El contador sigue en 1 porque usó el cache